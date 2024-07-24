import importlib.metadata
import math
from numbers import Number
from typing import List, Optional, Union

try:
    import stats_arrays as sa
except ImportError:
    sa = None

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


def matcher(source: dict, target: dict, fields: Optional[List[str]]) -> bool:
    return all(
        target.get(key) == value
        for key, value in source.items()
        if (not fields or key in fields)
        and key != "allocation"
    )


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
