from collections import defaultdict
import functools
from typing import *
from copy import deepcopy

from django.db.models.fields.related_descriptors import ManyToManyDescriptor
from django.db.models import Q,QuerySet,Model,ManyToManyField

from . import lookup_helpers

from .model_importer import ModelImporter

class ImporterManager(object):

    #: TODO: This is repeated in the SystemImporter class
    def is_many_to_many(self, field: str, model: Model):
        if isinstance(getattr(model,field), ManyToManyField) or \
                isinstance(getattr(model,field),ManyToManyDescriptor):
            return True
        else:
            return False

    def __init__(self, importer: ModelImporter=None, create: bool=False, is_m2m: bool=False):
        #: How this manager is used outside itself depends less on the importer and hence the model, but more on
        #: its reverse relations
        self.importer = importer

        self.create = create

        self.kvs = defaultdict(list)
        self.objs: QuerySet = None

        self.m2m_field: DefaultDict[str,bool] = defaultdict(bool)
        for key in self.importer.dependent_imports.keys():
            if self.is_many_to_many(key, self.importer.model):
                self.m2m_field[key] = True

        #: (Maybe log every row, indicating if there is no error)
        #: If a given row as an error, it will get logged here: error types:
        #:       * validation error:{missing-field,typing issue}
        #:       * object with given parameters not found
        self.errors: Dict[int,Dict[str,str]] = {} #: Typing subject to change

        self.object_row_map: Dict[int,List[Dict]] = {}

    def update_kvs(self, field_name: str, value, row: int, col: int=0):
        """

        """
        typed_value = lookup_helpers.get_typed_value(
            self.importer.field_types[field_name],value
        )

        # For many to many filters
        if self.m2m_field[field_name] and not self.create:
            #: TODO: This branch needs some testing
            #:       --> assume there is a field that needs an image as a dependent import
            field_name = f'{field_name}__in'

        if self.m2m_field[field_name] and type(typed_value) != list:
            typed_value = [typed_value]

        if self.kvs[row] and col < len(self.kvs[row]):
            self.kvs[row][col].update({field_name: typed_value})
        else:
            self.kvs[row].append({field_name: typed_value})

    def get_latest_row(self):
        #: This is incremented externally, because it is from that perspective that it will be known whether
        #: one is managing something that is many to many or not
        return max(self.kvs.keys())

    def get_available_rows(self):
        """
        Find all available objects given the key/values that have been provided thus far.

        TODO: This method needs some improvement in code readability
              * Should document limitations with using m2m fields
        """
        if not self.kvs:
            return None

        #: Building up query object for filtering, and object_row_map to map the results to each clause in the query
        query = Q(**self.kvs[0][0])
        self.object_row_map.update({0:[]})
        self.object_row_map[0].append({'query': query })

        for kv in self.kvs[0][1:]:
            query |= Q(**kv)
            self.object_row_map[0].append({'query': Q(**kv)})

        for i in range(1,len(self.kvs.keys())):
            for kv in self.kvs[i]:
                query |= Q(**kv)
                if i not in self.object_row_map.keys():
                    self.object_row_map.update({i:[]})
                self.object_row_map[i].append({'query': Q(**kv) })

        self.objs = self.importer.model.objects.filter(query)

        for row,dct_list in self.object_row_map.items():

            for i,dct in enumerate(dct_list):
                obj = self.objs.filter(dct['query']).first()

                self.object_row_map[row][i]['available'] = True if obj else False
                self.object_row_map[row][i]['obj'] = obj

    def get_objects_from_rows(self):
        """
        This is really going to be for the 'root' object (i.e. the object actually getting imported).
        """
        if not self.create:
            raise ValueError('This should only be called for model managers associated with new objects, '
                             'not dependent objects')

        #: Check for m2m fields first:
        m2m_keys = []

        for k,v in self.kvs[0][0].items():
            if self.m2m_field[k]:
                m2m_keys.append(k)
        m2m_objects = defaultdict(dict)

        objects = []
        #: Collect objects; if any have many to many fields, document them
        for row in range( self.get_latest_row() + 1 ):

            #: If there are any many to many fields, store each list object, and remove them from the main object
            #:    for an initial create.
            for k in m2m_keys:

                m2m_objects[row]['objs'] = defaultdict(dict)

                m2m_objects[row]['objs'][k] = deepcopy(self.kvs[row][0][k])
                del self.kvs[row][0][k]

            if m2m_keys:
                m2m_objects[row]['query'] = Q(**self.kvs[row][0])

            objects.append(
                self.importer.model(**self.kvs[row][0])
            )

        if m2m_keys:
            self.importer.model.objects.bulk_create(objects)
            queries = [m2m_objects[row]['query'] for row in m2m_objects.keys()]

            query = queries.pop()
            for q in queries:
                query |= q

            objects = []
            pk_objects = self.importer.model.objects.filter(query)

            for row in m2m_objects.keys():

                obj = pk_objects.filter(m2m_objects[row]['query']).first()
                for k in m2m_keys:
                    #: USER BE WARNED:  Each one of these operations requires a trip to the database
                    getattr(obj,k).set(m2m_objects[row]['objs'][k])

                objects.append(
                    obj
                )

        #: Returns either, a list of uncreated objects, or a list of created objects, with m2m attached and saved
        return objects

    def get_objs(self, row: int) -> List[Dict]:
        #: TODO: simply return the row, and add error checking outside this method
        return [e['obj'] for e in self.object_row_map[row]]