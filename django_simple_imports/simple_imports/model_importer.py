from typing import *
from collections import OrderedDict

from django.db import models

class ModelImporter(object):
    """
    Essentially defines a node in a dependency graph of models to import.
    """
    model: models.Model = None

    dependent_imports: OrderedDict = OrderedDict()

    #: If this is true, and this object represents an object being created, it will bulk create the associated models
    #:         before returning them
    auto_create: bool = False

    auto_create_m2m: bool = True #: It means you bulk create all

    #: TODO: Perhaps there should be a separate class variable required_fields_for_create (to distinguish what should
    #:       be necessary for getting vs. creating)
    #:       It's assumed that taken together, these will return the unique tuple from the model table
    required_fields: tuple = None

    #: From this you could infer modifiers __iexact, __contains, etc
    field_types: Dict[str,type] = dict()

    def validate(self):
        if not self.model:
            return False
        if not self.required_fields and not self.dependent_imports.keys():
            return False
        return True