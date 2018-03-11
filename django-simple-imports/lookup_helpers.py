#
# def get_modifier(filter_value):
#     if isinstance(filter_value,str):
#         return '__iexact'
#     return ''
#
#
# def update_kvs(kvs):
#     new_dict = {}
#     for k,v in kvs.items():
#         k = "{}{}".format(k, get_modifier(v))   #: TODO: Eventually grab this from a type dict
#         new_dict[k] = v
#     return new_dict

from datetime import date,datetime
from dateutil.parser import parse as parsedt
from decimal import Decimal
from django.db.models import Model

def get_typed_value(datatype,value):

    if datatype == date:
        return parsedt(value).date()
    if datatype == datetime:
        return parsedt(value)
    if datatype == Decimal:
        return Decimal(value)
    if datatype == float:
        return float(value)

    return value #: Returns string content as is
