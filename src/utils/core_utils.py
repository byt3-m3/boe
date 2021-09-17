from copy import deepcopy
from uuid import uuid5, NAMESPACE_URL

def clone_item(item) -> object:
    return deepcopy(item)

def make_id(domain, key):
    return uuid5(NAMESPACE_URL, f'{domain}/{key}' )