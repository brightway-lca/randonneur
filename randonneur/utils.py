import math
from collections.abc import Iterable, Mapping
from numbers import Number
from typing import Any, List, Optional

try:
    import stats_arrays as sa
except ImportError:
    sa = None

from .errors import MultipleTransformations

ALL_VERBS = ["create", "delete", "replace", "update", "disaggregate"]
SAFE_VERBS = ["update", "replace", "disaggregate"]


def apply_mapping(migrations: dict, mapping: dict, verbs: List[str]) -> dict:
    """Apply the label changes in `mapping` to the transformations in `migrations`."""
    if "source" in mapping:
        for verb in verbs:
            for transformation in migrations.get(verb, []):
                for key, value in mapping["source"].items():
                    if key in transformation["source"]:
                        transformation["source"][value] = transformation["source"].pop(key)
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
                            transformation["target"][value] = transformation["target"].pop(key)
    return migrations


def rescale_edge(edge: dict, factor: Number) -> dict:
    """Rescale edges, including formulas and uncertainty values, by a constant factor"""
    if not isinstance(factor, Number):
        raise ValueError(f"Can't rescale by non-number `factor` {factor}")
    if edge.get("formula"):
        edge["formula"] = "({}) * {}".format(edge["formula"], factor)

    # Special cases
    if "uncertainty type" not in edge:
        if "amount" in edge:
            edge["amount"] *= factor
        return edge
    elif factor == 0:
        edge["amount"], edge["uncertainty type"] = 0, sa.UndefinedUncertainty.id
        for attr in ("minimum", "maximum", "scale", "shape", "loc"):
            if attr in edge:
                del edge[attr]
        return edge

    # stats_arrays uncertainty
    if edge["uncertainty type"] in (sa.UndefinedUncertainty.id, sa.NoUncertainty.id):
        edge["amount"] = edge["loc"] = factor * edge["amount"]
    elif edge["uncertainty type"] == sa.NormalUncertainty.id:
        edge["amount"] = edge["loc"] = factor * edge["amount"]
        edge["scale"] *= factor
    elif edge["uncertainty type"] == sa.LognormalUncertainty.id:
        edge["amount"] = factor * edge["amount"]
        edge["loc"] = math.log(abs(edge["amount"]))
        if edge["amount"] < 0:
            edge["negative"] = True
        elif "negative" in edge:
            del edge["negative"]
    elif edge["uncertainty type"] == sa.TriangularUncertainty.id:
        edge["minimum"] *= factor
        edge["maximum"] *= factor
        if edge["minimum"] > edge["maximum"]:
            edge["minimum"], edge["maximum"] = edge["maximum"], edge["minimum"]
        if "amount" in edge:
            edge["amount"] = edge["loc"] = factor * edge["amount"]
        else:
            edge["amount"] = edge["loc"] = (edge["minimum"] + edge["maximum"]) / 2
    elif edge["uncertainty type"] == sa.UniformUncertainty.id:
        edge["minimum"] *= factor
        edge["maximum"] *= factor
        if edge["minimum"] > edge["maximum"]:
            edge["minimum"], edge["maximum"] = edge["maximum"], edge["minimum"]
        if "amount" in edge:
            edge["amount"] *= factor
        else:
            edge["amount"] = edge["loc"] = (edge["minimum"] + edge["maximum"]) / 2
    else:
        raise ValueError(f"Edge can't be automatically rescaled:\n\t{edge}")
    return edge


def right_case(value: Any, case_sensitive: bool) -> Any:
    if isinstance(value, str) and not case_sensitive:
        return value.lower()
    else:
        return value


class FlexibleLookupDict(Mapping):
    def __init__(
        self, input_data: Iterable[dict], fields_filter: Optional[List[str]], case_sensitive: bool
    ):
        """A dictionary that allow for more flexible matching of dictionaries against other dicts.

        We need to match a dictionary against another dictionary, but the other dictionary doesn't
        have a fixed set of keys - they can vary across all the possibilities. We therefore allow
        matching based on each unique combination of keys present.

        If `fields_filter` is given, then only consider keys present in that list.

        If `case_sensitive`, then do case-sensitive matching when comparing strings."""
        self._case_sensitive = case_sensitive
        self._field_combinations = set()
        self._dict = {}

        if fields_filter:
            fields_filter = set(fields_filter)

        for obj in input_data:
            fields = set(obj["source"]).difference({"allocation"})
            if fields_filter:
                fields = fields.intersection(fields_filter)
            self._field_combinations.add(tuple(sorted(fields)))
            key = tuple(
                [right_case(obj["source"][field], case_sensitive) for field in sorted(fields)]
            )
            if key in self._dict:
                raise MultipleTransformations(
                    f"Found multiple transformations for following field inputs: {key}"
                )
            self._dict[key] = obj

    def __getitem__(self, obj: dict) -> dict:
        if not isinstance(obj, dict):
            raise ValueError

        for field_combination in self._field_combinations:
            try:
                return self._dict[
                    tuple(
                        [
                            right_case(obj.get(field), self._case_sensitive)
                            for field in field_combination
                        ]
                    )
                ]
            except KeyError:
                continue

        raise KeyError

    def __len__(self) -> int:
        return len(self._dict)

    def __iter__(self) -> Iterable:
        return iter(self._dict)
