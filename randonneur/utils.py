import importlib.metadata
from typing import Union


def get_version_tuple() -> tuple:
    def as_integer(obj: str) -> Union[int, str]:
        try:
            return int(obj)
        except ValueError:
            return obj

    return tuple(
        as_integer(v)
        for v in importlib.metadata.version("randonneur").strip().split(".")
    )


def as_tuple(obj, fields):
    def converter(value):
        if isinstance(value, list):
            return tuple(value)
        else:
            return value

    return tuple([converter(obj.get(field)) for field in fields])


def matcher(source, target):
    return all(target.get(key) == value for key, value in source.items())


def maybe_filter(maybe_dict, dataset):
    if maybe_dict is None:
        return True
    else:
        return matcher(maybe_dict, dataset)
