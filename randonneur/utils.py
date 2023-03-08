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
