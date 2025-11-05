from datetime import datetime
from pprint import pformat
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from randonneur.errors import UnmappedData

VERBS = {"create", "replace", "update", "delete", "disaggregate"}


class Contributor(BaseModel):
    title: str
    roles: List[str]
    path: str


class MappingFields(BaseModel):
    expression_language: str = Field(alias="expression language")
    labels: Dict[str, Union[str, list, None]]


class DatapackageMetadata(BaseModel):
    """Validate given Datapackage metadata.

    Pydantic gives us nice error messages for free."""

    name: str
    description: str
    source_id: Optional[str] = None
    target_id: Optional[str] = None
    homepage: Optional[str] = None
    created: Optional[datetime] = datetime.now()
    version: str
    licenses: List[Dict[str, str]]
    graph_context: List[str]
    contributors: List[Contributor] = Field(min_length=1)


def validate_data_for_verb(verb: str, data: list, mapping: dict) -> None:
    if verb not in VERBS:
        raise ValueError(f"Transformation verb {verb} must be one of {VERBS}")

    if verb != "create":
        all_source_keys = set(mapping["source"]["labels"])
    all_target_keys = set(mapping["target"]["labels"])

    for element in data:
        if verb != "create":
            missing = set(element["source"]).difference(all_source_keys)
        else:
            missing = set([])

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
            missing = set(element["target"]).difference(all_target_keys).difference({"allocation"})
        if missing:
            raise UnmappedData(
                f"""
One of more `target` data attributes is not found in given mapping:
Mapping has the following fields:
{all_target_keys}
However, the given data also includes:
{missing}
In the data object:
{pformat(element)}
"""
            )
