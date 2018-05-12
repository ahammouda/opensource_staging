from . import lookup_helpers

from .model_importer import ModelImporter

#: This basically represents a state machine for each row of a csv file
#: TODO: Would be to incorporate some kind of caching facilities for this library
class ImporterManager:
    #: Essentially defines a single row state machine, determining whether you've obtained all the fields necessary to
    #: get an object associate with it's require fields
    def __init__(self,importer,create=False):

        self.importer: ModelImporter = importer

        self.kvs = {}
        """:type:dict"""

        self.create = create

        self.ready = False
        self.obj = None


    def add_kv(self,field_name,value):
        typed_value = value
        if field_name in self.importer.field_types.keys():
            typed_value = lookup_helpers.get_typed_value(
                self.importer.field_types[field_name],value
            )

        self.kvs.update({field_name:typed_value})  #: value can just be an object (like another base importer object)

        #: Check to see if you have all the required fields
        self.ready = True

        if self.importer.required_fields:
            for rf in self.importer.required_fields:
                if rf not in self.kvs.keys():
                    self.ready=False

        for rf in self.importer.dependent_imports.keys():
            if rf not in self.kvs.keys():
                self.ready=False

        #: If ready, get the object in question
        if self.ready and not self.create:
            #: TODO: Make this more robust by referencing type specifications in the import_configurations (once added)
            # self.kvs = lookup_helpers.update_kvs(self.kvs)

            #: TODO: Make this more robust: if a related object isn't found, this line needs to be skipped in the
            #:     calling function, and the lack of presence needs to be logged.
            try:
                self.obj = self.importer.model.objects.get(**self.kvs) #: Instead pass the importer.model into object cache w/kvs, and get that object
            except Exception as e:
                import pdb; pdb.set_trace()

        elif self.ready:
            self.obj = self.importer.model(**self.kvs)


    def update_kv_reference(self):
        #: This would probably be useful given some kind of caching features
        pass


    def get_object(self):
        return self.obj


    def reset_row(self):
        #: TODO: Should pass obj && kvs to self.object_cache or something
        self.kvs.clear()
        self.ready = False
        self.obj = None


# #: assume that in system_importer:
# self.importers_to_manager = {}
# self.managers = []
# for i,imp in enumerate(self.importers): #: be sure to do this in topoligically sorted order
#     self.managers.append(ImporterManager(imp))
#     self.importers_to_manager[imp] = self.managers[i]

#: Need to know which basemanagers correspond to fields in higher level managers?

#: CONTEXT: Inner loop of iterating through lines of csv file
# visited_managers = set() #: Set should be unnecessary ()
# fields = row.split(",")
# #: For loop handles all importers without dependent imports
# for i,v in enumerate(fields):
#     field_name,importer = index_to_name_importer[i] #: maps csv index to the (field_name,importer)
#     self.importers_to_manager[importer].add_kv(field_name,v) #: Add k,v from the file
#     if self.importers_to_manager[importer].ready:
#         visited_managers.add(self.importers_to_manager[importer])
#
# for manager in set(self.managers)-visited_managers: #: You will need to do this in order of topological sort
#     for fname,importer in manager.importer.dependent_imports.items():
#         manager.add_field(fname,self.importers_to_manager[importer].get_object())
#
# visited_managers.clear()
# for manager in self.managers:
#     manager.reset_row()
