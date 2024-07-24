import importlib.metadata
from typing import List, Union

ALL_VERBS = ["create", "delete", "replace", "update", "disaggregate"]
SAFE_VERBS = ["update", "replace", "disaggregate"]


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


def matcher(source, target):
    return all(target.get(key) == value for key, value in source.items())


def maybe_filter(maybe_dict, dataset):
    if maybe_dict is None:
        return True
    else:
        return matcher(maybe_dict, dataset)


def apply_mapping(migrations: dict, mapping: dict, verbs: List[str]) -> dict:
    """Apply the label changes in `mapping` to the transformations in `migrations`."""
    if "source" in mapping:
        for verb in verbs:
            for transformation in migrations.get(verb, []):
                for key, value in mapping["source"].items():
                    if key in transformation["source"]:
                        transformation["source"][value] = transformation["source"].pop(
                            key
                        )
    if "target" in mapping:
        for verb in verbs:
            if verb == "disaggregate":
                for transformation_list in migrations.get(verb, []):
                    for transformation in transformation_list["targets"]:
                        for key, value in mapping["target"].items():
                            if key in transformation:
                                transformation[value] = transformation.pop(key)
            elif verb in ("create", "delete"):
                continue
            else:
                for transformation in migrations.get(verb, []):
                    for key, value in mapping["target"].items():
                        if key in transformation["target"]:
                            transformation["target"][value] = transformation[
                                "target"
                            ].pop(key)
    return migrations
