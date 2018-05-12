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
from typing import *
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

    return value #: Returns string or object content as is


#: Note right now this is not being used anywhere, but it is an interesting aside on the use of many to many fields
def filter_objects_exactly_by_m2m(m2m_objects: List[Model], reverse_attribute)->List[Model]:
    # This works only when the associated list of the m2m field is a unique superset of other objects
    # If you want to filter the fields that ONLY have the m2m_objects input (and no more), this will fail
    sets = []
    reverse_attribute = f'{reverse_attribute}_set'
    for o in m2m_objects:
        reverse_manager = getattr(o,reverse_attribute, None)

        if not reverse_manager:
            raise RuntimeError(f'Attribute {reverse_attribute} is not available on these m2m objects.')

        sets.append(
            set([io for io in reverse_manager.all()])
        )
    return list(set.intersection(sets))