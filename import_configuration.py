# from django.db import models
# from django.contrib.auth.models import User
# from website.datafeed.fiserv.models import FiservSecurity
# from website.apps.users.models import UserProfile
# from website.apps.cac.models import ClassTag, AssetClassification
# from website.apps.firms.models import Firm
#
#
# class ModelImporter:
#     """
#     Essentially defines a node in a dependency graph of models to import
#     """
#     model = None
#     """:type:models.Model"""
#
#     bases = None
#     """:type:dict[str,tuple]"""
#
#     dependent_imports = None
#     """:type:dict[str,ModelImporter]"""
#
#     required_fields = None
#     """:type:tuple(str)"""
#
#     def __init__(self):
#         pass
#
#     def validate(self):
#         if not self.bases.keys() and not self.required_fields and not self.dependent_imports.keys():
#             return False
#         return True
#
#
# #: All we're doing here is defining the closure of the system of tables we want to import.  What we want to do above
# #: is be able to infer ordering, and dependence from these structures in order to get dependent models, and create
# #: those above in the hierarchy.
# class TagImporter(ModelImporter):
#     model = ClassTag
#     bases = {
#         'firm': (Firm, 'short_name'),
#     }
#     required_fields = ('name')
#
#
# class UserProfileImporter(ModelImporter):
#     model = UserProfile
#     bases = {
#         'user': (User,'username')
#     }
#     required_fields = ('user')
#
#
# class AssetClassImporter(ModelImporter):
#     model = AssetClassification
#     bases = {
#         #: To remove heterogeneity of interface, these bases could just as easily be Their own importers, with 2nd elements
#         #: of tuple as "required_fields", and first element set to "model"
#         'security':(FiservSecurity,'symbol'),
#         'firm': (Firm, 'short_name'),
#         'created_by_user': (User,'username')
#     }
#
#     #: The structure implied here would require some amount of recursion
#     dependent_imports = {
#         'tag': TagImporter,
#         'created_by_profile': UserProfileImporter,
#     }
#
#
# # class SystemImporter:
# #
# #     #: TODO: Make this list of importers an input to __init__()
# #     importers = (AssetClassImporter, TagImporter)
# #
# #     def __init__(self,csvfilepath=None):
# #         if not csvfilepath:
# #             #: TODO: Want to return instructions preparing the necessary csvfiles
# #             pass
# #
# #         self.csvfile = open(csvfilepath,'r')
# #         self.lines = self.csvfile.readlines()
# #         self.csv_field_labels = []
# #
# #         self.n_base_fields = 0
# #         self.n_dependent_fields = 0
# #         self.n_required_fields = 0
# #
# #
# #     def get_csv_order(self):
# #         self.csv_field_labels = []
# #         self.field_table = {}
# #         count = 0
# #
# #         #: This should really be done after your depth first
# #         for i,model_field_name,base_field_name in enumerate(self.bases.items()):
# #
# #             self.field_table[model_field_name] = i #: To reference later when parsing csv
# #             self.csv_field_labels.append(base_field_name)
# #             count=i
# #
# #         #: TODO: here you want to drill down into the references of the dependent keys
# #
# #
# #         self.csv_field_labels.append(key)
# #
# #         return ','.join(self.csv_field_labels)
# #
# #
# #     #: TODO: Need to check that this conforms to the structure above: Might need to pass a
# #     #:              counter and the field table into this function.  Should also rename this.
# #     def get_leaves(self,importer,count):
# #         inner_imports = getattr(importer, 'dependent_imports', None)
# #         if not inner_imports:
# #             #: These should be the leaves;  May need to also return an ordering here.
# #             fields = [f for f in importer.required_fields]
# #             count += len(fields)
# #             return count , ','.join(fields)
# #         else:
# #             #: Only think this works if you:
# #             return get_leaves(tuple[0],count)
# #             fields = ''
# #             for field,tuple in inner_imports.items():
# #                 icount, ifields = get_leaves(tuple[0],count)
# #                 fields = fields + ',' + ffields
# #
# #                 count+=icount
# #
# #             fields = fields + ','.join([f for f in importer.required_fields])
# #             return fields
# #
# #         #: Bottom Up Pseudocode:
# #         # for field,tuple in self.dependent_imports.items():
# #         #     inner_imps = getattr(tuple[0], 'dependent_imports', None)
# #         #     if inner_imps:
# #         #         for ifield,ituple in inner_imps.items():
# #         #             i_inner_imps = getattr(ituple[0], 'dependent_imports', None)
# #         #             if i_inner_imps:
# #         #                 for iifield,iituple in i_inner_imps.items():
# #         #                     pass
# #
# #
# #
# #     #: If you call this for the penultimate in whatever import hierarchy you're constructing, should be able to trace
# #     #: back through each sub importer
# #     def import_models(self):
# #         #: This can be flat if you've prepped the csv ordering properly
# #         for line in self.lines:
# #             for i,item in enumerate(line.split(',')):
# #                 pass
