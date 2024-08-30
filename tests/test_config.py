import pytest
from pydantic import ValidationError

from randonneur import MigrationConfig


def test_migration_config_valid():
    assert MigrationConfig()
    assert MigrationConfig(
        mapping={"source": {"foo": "bar"}, "target": {"1": "2"}},
        node_filter=lambda x: True,
        edge_filter=lambda x: False,
        fields=["name", "reference product"],
        verbose=True,
        edges_label="this",
        verbs=["replace", "delete"],
        case_sensitive=True,
    )


def test_migration_config_invalid():
    with pytest.raises(ValidationError):
        MigrationConfig(mapping=["foo", "bar"])
