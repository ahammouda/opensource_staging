from typing import Dict, List, Tuple
from collections import defaultdict

from django.db import models
from django.db.models.fields.related_descriptors import ManyToManyDescriptor

from dotdict import DotDict

from .sorter import Sorter
from .model_importer import ModelImporter
from .importer_manager_v2 import ImporterManager

import pdb

#: TODO: Document the necessity of these being differently
M2M_DELIMITER = ';'
DEFAULT_DELIMITER = ','

class SystemImporter:

    def __init__(self, importers: List[ModelImporter], csvfilepath: str):
        """

        :param importers:   This must include all necessary importers needed for all dependencies to be met
                            (i.e. Must be the transitive closure of necessary dependencies)
        :param csvfilepath:
        """
        self.importers = importers

        #: Initialize dependency structure of imports
        self.graph = []
        """:type:list[DotDict]"""

        self.sorted_vertices: List[DotDict] = []

        self._construct_adjacency_graph()
        self._topologically_sort_graph()

        #: Initialize csv reading state machines (managers)
        self.managers = []
        """:type:list[ImportManager]"""

        self.importers_to_manager: Dict[ModelImporter,ImporterManager] = {}
        """:type:dict[ModelImporter:ImportManager]"""

        self.create_model = None
        """:type:models.Model"""

        self._initialize_managers()

        #: Setup csv input fields and mappings back to managers
        self.csv_import_format = ""
        """:type:str"""

        self.location_to_importer = {}
        """:type:dict[int,ModelImporter]"""

        self.location_to_csv_field = {}
        """:type:dict[int,str]"""

        self.csv_import_format = self._get_import_fields()

        self.new_objects: List[models.Model] = []


        self.candidate_objects: List[models.Model] = []

        self.lines = []
        """:list[str]"""

        if csvfilepath:
            self.file_path = csvfilepath

            with open(self.file_path, 'r') as f:
                self.lines = f.readlines()

        else:
            raise RuntimeError("Must provide a file with data in the format: {}".format(self.csv_import_format))


    def _construct_adjacency_graph(self):

        for i,vertex in enumerate(self.importers):
            self.graph.append(DotDict({
                'id':i,
                'Adj':[],
                'p':None,
                'color':"WHITE",
                'd':0,
                'f':0,
                'importer':vertex
            }))

        #: Once this for loop is complete, circle back and add to the Adjacencies
        for vertex in self.graph:

            #: Should return a dictionary
            neighbors = vertex.importer.dependent_imports

            if not neighbors:
                continue

            #pdb.set_trace()
            for field,importer in neighbors.items(): #: This is deterministic and therefore the results are.
                inner_vertex = next((x for x in self.graph if x.importer==importer),None)
                assert inner_vertex is not None
                vertex.Adj.append(self.graph[inner_vertex.id])


    def _topologically_sort_graph(self):
        sorter = Sorter()
        sorter.dfs(self.graph)
        self.sorted_vertices = sorter.sorted_vertices


    def _initialize_managers(self):
        for i,v in enumerate(self.sorted_vertices):
            #: N.B: This Assume that only one model type is being created for each import (everything else defines getters
            #:      for FK fields or fields of the new object)
            if i == len(self.sorted_vertices)-1:
                create = True
            else:
                create = False

            self.managers.append(
                ImporterManager(v.importer,create=create)
            )
            self.importers_to_manager[v.importer] = self.managers[i]

        self.create_model = self.sorted_vertices[-1].importer.model


    def _get_import_fields(self):
        fields = ""
        count = 0; #: TODO: Move to enumerated field
        for v in self.sorted_vertices:
            if v.importer.required_fields is None:
                continue

            for field in v.importer.required_fields:

                self.location_to_importer[count] = v.importer

                self.location_to_csv_field[count] = field

                fields = f'{fields}{field},'
                count+=1

        return fields

    def is_many_to_many(self, field: str, model: models.Model):
        if isinstance(getattr(model,field),models.ManyToManyField) or \
                isinstance(getattr(model,field),ManyToManyDescriptor):
            return True
        else:
            return False

    def import_data(self):
        #: TODO: Make it so you don't need to assume there's no header
        for row,line in enumerate(self.lines):

            visited_managers = set()
            fields = line.split(DEFAULT_DELIMITER)

            #: Iterate accross row of csv file
            for i,value in enumerate(fields):
                _field = self.location_to_csv_field[i]
                if i<len(self.location_to_importer):
                    _importer = self.location_to_importer[i]
                else:
                    #: TODO:  This should be done only if the object has required fields <- it could be that
                    #:(TODO)  this last field is of a related object of the create model
                    self.candidate_objects.append(self.create_model())
                    setattr(self.candidate_objects[row],_field,value)

                #region Handle Parsing out M2M relationships if present
                if self.is_many_to_many(_field):
                    m2m_refs = value.split(M2M_DELIMITER)
                    for ref in m2m_refs:
                        self.importers_to_manager[_importer].add_kv(_field, ref)
                #endregion

                #: TODO: Shouldn't this not be called if _field is_m2m
                self.importers_to_manager[_importer].add_kv(_field, value.replace('\n',''))

                # if self.importers_to_manager[_importer].ready:
                #     visited_managers.add(self.importers_to_manager[_importer])

            # #: You should be able to build up objects that had any 'getter' dependencies contained in the csv import
            # for manager in self.managers:
            #     if manager in visited_managers:
            #         continue
            #
            #     for fname, importer in manager.importer.dependent_imports.items():
            #         manager.add_kv(fname, self.importers_to_manager[importer].get_object())
            #
            # #: At this point root level obect won't exist b/c no other object depends on it.
            # #: Add the new populated object to the list of objects to create:
            # self.new_objects.append(
            #     self.managers[-1].get_object()
            # )
            #
            # #: Reset managers/manager state machines
            # visited_managers.clear()
            # for manager in self.managers:
            #     manager.reset_row()

        # Read from DB:
        for manager in self.importers_to_manager.values():
            manager.get_available_rows()

        # Map available related data to object being imported
        for model_instance in self.candidate_objects:
            for manager in self.importers_to_manager.values():
                #: TODO:
                # for row in range(len(self.lines)):
                objs = manager.get_objs() #: row
                available_objs = [obj['obj'] for obj in objs if obj['available']]
                if len(objs) !=len(available_objs):
                    print(f'TODO: Log which kv pairs could not retreive objects')
                    # find some
                    break;
                #: TODO: Need some attribute to related manager dictionary
                if len(objs)>1:
                    setattr(model_instance,self.manager_to_attribute[manager],available_objs)
                else:
                    setattr(model_instance,self.manager_to_attribute[manager],available_objs[0])

    def store_data(self):
        self.create_model.objects.bulk_create(self.new_objects)
