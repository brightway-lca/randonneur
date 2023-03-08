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
