from typing import List

from randonneur.utils import apply_mapping


def test_apply_mapping_basic():
    given = {"replace": {}, "disaggregate": {}, "create": {}}


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


{
    "name": "generic-brightway-units-normalization",
    "description": "Standard units normalization used in most Brightway projects",
    "contributors": [
        {"title": "Chris Mutel", "path": "https://chris.mutel.org/", "role": "author"}
    ],
    "created": "2024-07-25T06:47:10.575370+00:00",
    "version": "1.0.0",
    "licenses": [
        {
            "name": "CC-BY-4.0",
            "path": "https://creativecommons.org/licenses/by/4.0/legalcode",
            "title": "Creative Commons Attribution 4.0 International",
        }
    ],
    "graph_context": ["nodes", "edges"],
    "mapping": {
        "source": {"expression language": "JSONPath", "labels": {"unit": "Node.unit"}},
        "target": {"expression language": "JSONPath", "labels": {"unit": "Node.unit"}},
    },
    "source_id": "bw_interfaces_schemas-1",
    "target_id": "bw_interfaces_schemas-1",
    "homepage": "https://github.com/brightway-lca/bw_interface_schemas",
    "replace": [
        {"source": {"unit": "a"}, "target": {"unit": "year"}},
        {"source": {"unit": "h"}, "target": {"unit": "hour"}},
        {"source": {"unit": "ha"}, "target": {"unit": "hectare"}},
        {"source": {"unit": "hr"}, "target": {"unit": "hour"}},
        {"source": {"unit": "kg"}, "target": {"unit": "kilogram"}},
    ],
}
