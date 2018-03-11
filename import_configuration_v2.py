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


#: App specific
from django.contrib.auth.models import User
from website.datafeed.fiserv.models import FiservSecurity
from website.apps.users.models import UserProfile
from website.apps.cac.models import ClassTag, AssetClassification
from website.apps.firms.models import Firm

class FirmImporter(ModelImporter):
    model = Firm
    required_fields = ('short_name__iexact',)


class UserImporter(ModelImporter):
    model = User
    required_fields = ('username__iexact',)


class SecurityImporter(ModelImporter):
    model = FiservSecurity
    #: Be nice to be able to define OR conditions for requirements for models like this
    required_fields = ('symbol__iexact',)


class TagImporter(ModelImporter):
    model = ClassTag

    required_fields = ('name__iexact',) #: TODO: Add type information to all the required fields

    dependent_imports = OrderedDict({
        'firm': FirmImporter
    })


class UserProfileImporter(ModelImporter):
    model = UserProfile

    #: Must be OneToOne field relation for this to work without required_fields ??
    dependent_imports = OrderedDict({
        'user': UserImporter
    })


class AssetClassImporter(ModelImporter):
    model = AssetClassification

    #: The structure implied here would require some amount of recursion
    #: TODO: In python 3.6 ordering will be implicit in kwargs inputs
    dependent_imports = OrderedDict(sorted({
        'tag': TagImporter,
        'created_by_profile': UserProfileImporter,
        'security': SecurityImporter,
        'firm': FirmImporter,
        'created_by_user': UserImporter
    }.items(),key=lambda t: t[0]))



################################################################################################################
### HF importers

from decimal import Decimal
from datetime import date
from website.apps.hfaccounting.models import HedgeFundCostValue

class HedgeFundCostValueImporter(ModelImporter):
    model = HedgeFundCostValue

    required_fields = ('account_number','symbol','cost_value','as_of_date')

    field_types = {
        'account_number': str,
        'symbol': str,
        'cost_value': Decimal,
        'as_of_date': date
    }
