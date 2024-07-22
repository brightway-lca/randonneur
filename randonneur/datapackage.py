import os
from typing import Optional
from pathlib import Path
import json
from datetime import datetime, timezone

from .errors import UnmappedData, ValidationError


CONTRIBUTORS_REQUIRED_FIELDS = {'title', 'role', 'path'}
VERBS = {"create", "replace", "update", "delete", "disaggregate"}
CC_BY = [
    {
        "name": "CC BY 4.0",
        "path": "https://creativecommons.org/licenses/by/4.0/",
        "title": "Creative Commons Attribution 4.0 International",
    }
]


class Datapackage:
    def __init__(self, name: str, description: str, contributors: list, mapping_source: dict, mapping_target: dict, created: Optional[datetime] = None, version: str = "1.0.0", licenses: Optional[list] = None):
        self.name = name
        self.description = description
        self.contributors = contributors
        self.created = created or datetime.now(timezone.utc).isoformat()
        self.mapping = {"source": mapping_source, "target": mapping_target}
        self.licenses = licenses or CC_BY
        self.version = version
        self.data = {}

        if not self.contributors:
            raise ValidationError("Must provide at least one contributor")
        if not all(contributor.get(field) for contributor in self.contributors for field in CONTRIBUTORS_REQUIRED_FIELDS):
            raise ValidationError(f"Contributors must all have all of the following fields: {CONTRIBUTORS_REQUIRED_FIELDS}")

    def metadata(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "contributors": self.contributors,
            "created": self.created.isoformat() if isinstance(self.created, datetime) else self.created,
            "version": self.version,
            "licenses": self.licenses,
            "mapping": self.mapping
        }

    def add_data(self, verb: str, data: list) -> None:
        if verb not in VERBS:
            raise ValueError(f"Transformation verb {verb} must be one of {VERBS}")
        if verb not in self.data:
            self.data[verb] = []

        # TBD: Check that keys are in mapping
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
