import math
from collections.abc import Iterable, Mapping
from numbers import Number
from typing import Any, List, Optional

import stats_arrays as sa

from .errors import MultipleTransformations, ConflictingConversionFactors

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
    """Convert strings to lower case, and lists to tuples."""
    if isinstance(value, str) and not case_sensitive:
        return value.lower()
    elif isinstance(value, (tuple, list)) and not case_sensitive:
        return tuple([v.lower() if isinstance(v, str) else v for v in value])
    elif isinstance(value, (tuple, list)) and not case_sensitive:
        return tuple(value)
    else:
        return value


class FlexibleLookupDict(Mapping):
    def __init__(
        self,
        input_data: Iterable[dict],
        fields_filter: Optional[List[str]] = None,
        case_sensitive: bool = False,
    ):
        """A dictionary that allow for more flexible matching of dictionaries against other dicts.

        `input_data` is a dictionary like `{"foo": {"first": True, "bar": 42}}`. We want to match
        this input against `{'first': True}` and get back `foo`. Here is an examples:

        ```python
        fld = FlexibleLookupDict(
            input_data=[
                {"source": {"foo": "a", "bar": "b"}},
                {"source": {"foo": "b"}},
            ]
        )
        fld[{"foo": "b"}] == {"source": {"foo": "b"}}
        >>> True
        ```

        For real data we would have input data with both `source` and `target` (or `targets` for
        disaggregation) keys. This class makes the **strong assumption** that `input_data` has
        `source` and `target`/`targets` keys.

        We need to match a dictionary against another dictionary, but the other dictionary doesn't
        have a fixed set of keys - they can vary across all the possibilities. We therefore allow
        matching based on each unique combination of keys present.

        If `fields_filter` is given, then only consider keys present in that list.

        ```python
        fld = FlexibleLookupDict(
            input_data=[
                {"source": {"foo": "a", "bar": "b"}},
                {"source": {"foo": "b"}},
            ],
            fields_filter=["foo"]
        )
        fld[{"foo": "b", "other": "whatever"}] == {"source": {"foo": "b"}}
        >>> True
        ```

        If `case_sensitive`, then do case-sensitive matching on values (not keys) when comparing
        strings. Here is an example of a *case-insensitve* match:

        ```python
        fld = FlexibleLookupDict(
            input_data=[
                {"source": {"foo": "a", "bar": "b"}},
                {"source": {"foo": "b"}},
            ],
            case_sensitive=False
        )
        fld[{"foo": "B"}] == {"source": {"foo": "b"}}
        >>> True
        ```

        """
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
            try:
                # Short circuits to `KeyError` if not present
                # We don't bother examining if disaggregation is consistent, this shouldn't be
                # allowed full stop
                if "targets" in obj and self._dict[key]:
                    raise MultipleTransformations(f"""
Found multiple transformations including disaggregation for:
{obj['source']}
""")

                # `obj` is already present in the dictionary. This is OK, if the *functionally
                # equivalent* values are being added. We would like to reject this data
                # completely, but then we have to fix the input data ourselves, and... yuck.
                existing = {
                    key: right_case(value, case_sensitive)
                    for key, value in self._dict[key]["target"].items()
                }
                given = {
                    key: right_case(value, case_sensitive) for key, value in obj["target"].items()
                }
                if existing != given:
                    raise MultipleTransformations(
                        f"""
Found multiple transformations for following field inputs:
{obj['source']}

Targets:

{obj['target']}

{self._dict[key]['target']}
"""
                    )
                if "conversion_factor" in obj and "conversion_factor" not in self._dict[key]:
                    self._dict[key]["conversion_factor"] = obj["conversion_factor"]
                elif "conversion_factor" in obj and "conversion_factor" in self._dict[key]:
                    if not math.isclose(
                        obj["conversion_factor"],
                        self._dict[key]["conversion_factor"],
                        abs_tol=1e-2,
                        rel_tol=1e-2,
                    ):
                        raise ConflictingConversionFactors(f"""
Found at least two different conversion factors for the same transformation.
First: {obj["conversion_factor"]}
Second: {self._dict[key]["conversion_factor"]}
For conversion from: {obj["source"]}
To: {obj["target"]}
                        """)
            except KeyError:
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
