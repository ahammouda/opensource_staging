from collections import defaultdict
from typing import *
from copy import deepcopy

from django.db.models import Q,QuerySet

from . import lookup_helpers

from .model_importer import ModelImporter

class ImporterManager(object):
    """
    An importer manager's only job is to get a related objects at the end of or flags if the objects don't exist.
    (it is strictly lazy as in it only collects objects at the end) <- this may have some limitations.
              --> Try to architect s.t. you can swap such a manager out.

    The add_kv() function transitions a state machine, and increments the main data structure (self.kvs)

    self.kvs is used to populated self.object_row_map which is the data structure accessed from outside this model
    """

    def __init__(self, importer: ModelImporter=None, create: bool=False):
        #: How this manager is used outside itself depends less on the importer and hence the model, but more on
        #: its reverse relations
        self.importer = importer

        #: N.B: Right now, this isn't really used
        self.create = create

        self.row = 0

        self.kvs = defaultdict(list)
        self.objs: QuerySet = None

        self.object_row_map: Dict[int,List[Dict]] = {}

        self.current_kvs = {}

    def add_kv(self,field_name,value):
        typed_value = value

        if field_name in self.importer.field_types.keys():
            typed_value = lookup_helpers.get_typed_value(
                self.importer.field_types[field_name],value
            )

        self.current_kvs.update({field_name:typed_value})  #: value can just be an object (like another base importer object)

        self.ready = True

        if self.importer.required_fields:
            for rf in self.importer.required_fields:
                if rf not in self.current_kvs.keys():
                    self.ready=False

        if self.ready:
            self.kvs[self.row].append(
                deepcopy(self.current_kvs)
            )
            self.reset_state()

    def reset_state(self):
        self.current_kvs.clear()
        self.ready = False

    def increment_row(self):
        #: This is incremented externally, because it is from that perspective that it will be known whether
        #: one is managing
        self.row += 1

    def get_available_rows(self):
        """
        Find all available objects given the key/values that have been provided thus far.

        This might only be salient for 'base'/'node' objects.  Still need to ensure something like this plays nicely
        with
        Before you were getting related objects row by row, so now that you get them all at once in the last row, you
        need another iteration over each row system_importer_v2
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

    def get_objs(self,row: int) -> List[Dict]:
        return self.object_row_map[row]