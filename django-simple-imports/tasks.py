from website.helpers import load_django
load_django()

from invoke import task

@task()
def import_arbitrary():
    from adam_qa.importer_project.import_configuration_v2 import AssetClassImporter, UserProfileImporter, TagImporter, \
        UserImporter, \
        FirmImporter, SecurityImporter
    from adam_qa.importer_project.system_importer import SystemImporter

    import pdb

    path = "/Users/ahammouda/Bridge/development/dashboard/test_data/fmg_test_data.csv"
    importers = [AssetClassImporter, UserProfileImporter, TagImporter, UserImporter, FirmImporter, SecurityImporter]

    master_importer = SystemImporter(importers, csvfilepath=path)
    master_importer.import_data()
    pdb.set_trace()
    master_importer.store_data()


@task()
def import_hf_stuff():
    from adam_qa.importer_project.import_configuration_v2 import HedgeFundCostValueImporter
    from adam_qa.importer_project.system_importer import SystemImporter

    import pdb

    path = "/Users/ahammouda/Bridge/development/dashboard/test_data/DOA_HF_Cost_Basis_Updates.csv"
    importers = [HedgeFundCostValueImporter]

    master_importer = SystemImporter(importers, csvfilepath=path)
    master_importer.import_data()
    pdb.set_trace()
    master_importer.store_data()


@task()
def import_
