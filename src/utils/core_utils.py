from copy import deepcopy


def clone_item(item) -> object:
    return deepcopy(item)