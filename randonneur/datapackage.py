import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from randonneur.validation import (
    DatapackageMetadata,
    Contributors,
    MappingFields,
    validate_data_for_verb,
)
from randonneur.licenses import LICENSES


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
        self.licenses = licenses or [LICENSES["CC-BY-4.0"]]
        self.version = version
        self.data = {}
        self.graph_context = graph_context or ["edges"]

        for contributor in contributors:
            Contributors(**contributor)
        MappingFields(**mapping_source)
        MappingFields(**mapping_target)
        DatapackageMetadata(
            name=self.name,
            description=self.description,
            source_id=self.source_id,
            target_id=self.target_id,
            homepage=self.homepage,
            created=self.created,
            version=self.version,
            licenses=self.licenses,
            graph_context=self.graph_context,
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
        validate_data_for_verb(verb=verb, data=data, mapping=self.mapping)
        if verb not in self.data:
            self.data[verb] = []
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
