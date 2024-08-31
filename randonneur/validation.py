from datetime import datetime
from typing import List, Dict, Optional, Union

from pydantic import BaseModel, Field


class Contributors(BaseModel):
    title: str
    role: str
    path: str


class MappingFields(BaseModel):
    expression_language: str = Field(alias="expression language")
    labels: Dict[str, Union[str, list]]


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
