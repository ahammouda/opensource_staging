from collections import OrderedDict

from django.db import models

class ModelImporter:
    """
    Essentially defines a node in a dependency graph of models to import.
    This class is meant to be abstract
    """
    model = None
    """:type:models.Model"""

    dependent_imports = OrderedDict()
    """:type:OrderedDict[str,ModelImporter]"""

    #: TODO: Perhaps there should be a separate class variable required_fields_for_create (to distinguish what should be necessary for getting vs. creating)
    #: It's assumed that taken together, these will return the unique tuple from the model table
    required_fields = None
    """:type:tuple(str)"""

    #: From this you could infer modifiers __iexact, __contains, etc
    field_types = None
    """:type:dict[str,type]"""

    # def __init__(self):
    #     pass

    def validate(self):
        if not self.model:
            return False
        if not self.required_fields and not self.dependent_imports.keys():
            return False
        return True