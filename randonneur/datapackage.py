import json
import os
from datetime import datetime, timezone
from pathlib import Path
from pprint import pformat
from typing import Optional

from .errors import UnmappedData, ValidationError

CONTRIBUTORS_REQUIRED_FIELDS = {"title", "role", "path"}
VERBS = {"create", "replace", "update", "delete", "disaggregate"}
CC_BY = [
    {
        "name": "CC BY 4.0",
        "path": "https://creativecommons.org/licenses/by/4.0/",
        "title": "Creative Commons Attribution 4.0 International",
    }
]


class Datapackage:
    def __init__(
        self,
        *,
        name: str,
        description: str,
        contributors: list,
        mapping_source: dict,
        mapping_target: dict,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        homepage: Optional[str] = None,
        created: Optional[datetime] = None,
        version: str = "1.0.0",
        licenses: Optional[list] = None,
        graph_context: Optional[list] = None,
    ):
        self.name = name
        self.description = description
        self.contributors = contributors
        self.source_id = source_id
        self.target_id = target_id
        self.homepage = homepage
        self.created = created or datetime.now(timezone.utc).isoformat()
        self.mapping = {"source": mapping_source, "target": mapping_target}
        self.licenses = licenses or CC_BY
        self.version = version
        self.data = {}
        self.graph_context = graph_context or ["edges"]

        if not self.contributors:
            raise ValidationError("Must provide at least one contributor")
        if not all(
            contributor.get(field)
            for contributor in self.contributors
            for field in CONTRIBUTORS_REQUIRED_FIELDS
        ):
            raise ValidationError(
                f"Contributors must all have all of the following fields: {CONTRIBUTORS_REQUIRED_FIELDS}"
            )

    def metadata(self) -> dict:
        data = {
            "name": self.name,
            "description": self.description,
            "contributors": self.contributors,
            "created": self.created.isoformat()
            if isinstance(self.created, datetime)
            else self.created,
            "version": self.version,
            "licenses": self.licenses,
            "graph_context": self.graph_context,
            "mapping": self.mapping,
            "source_id": self.source_id,
            "target_id": self.target_id,
        }
        if self.homepage:
            data["homepage"] = self.homepage
        return data

    def add_data(self, verb: str, data: list) -> None:
        if verb not in VERBS:
            raise ValueError(f"Transformation verb {verb} must be one of {VERBS}")
        if verb not in self.data:
            self.data[verb] = []

        all_source_keys = set(self.mapping["source"]["labels"])
        all_target_keys = set(self.mapping["target"]["labels"])

        for element in data:
            missing = set(element["source"]).difference(all_source_keys)
            if missing:
                raise UnmappedData(
                    f"""
    One of more `source` data attributes is not found in given mapping:
    Mapping has the following fields:
{all_source_keys}
    However, the given data also includes:
{missing}
    In the data object:
{pformat(element)}
    """
                )
            if verb == "disaggregate":
                missing = (
                    set.union(*[set(obj) for obj in element["targets"]])
                    .difference(all_target_keys)
                    .difference({"allocation"})
                )
            elif verb == "delete":
                # No target element
                missing = None
            else:
                missing = (
                    set(element["target"]).difference(all_target_keys).difference({"allocation"})
                )
            if missing:
                raise UnmappedData(
                    f"""
    One of more `target` data attributes is not found in given mapping:
    Mapping has the following fields:
{all_source_keys}
    However, the given data also includes:
{missing}
    In the data object:
{pformat(element)}
    """
                )
        self.data[verb].extend(data)

    def to_json(self, filepath: Path) -> Path:
        if not isinstance(filepath, Path):
            filepath = Path(filepath)
        if filepath.suffix.lower() != ".json":
            filepath = filepath.parent / f"{filepath.name}.json"
        if not os.access(filepath.parent, os.W_OK):
            raise OSError(f"Can't write to directory {filepath.parent}")

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.metadata() | self.data, f, indent=2, ensure_ascii=False)

        return filepath
