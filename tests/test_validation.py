import datetime
from randonneur.validation import DatapackageMetadata, Contributors, MappingFields
from randonneur import Datapackage
import pytest
from pydantic import ValidationError


def test_contributors():
    Contributors(**{"title": "John", "role": "wrangler", "path": "example.com"})
    Contributors(**{"title": "John", "role": "wrangler", "path": "example.com", "extra": "ignore"})

    with pytest.raises(ValidationError):
        Contributors(**{"title": "John", "role": "wrangler"})


def test_mapping_fields():
    MappingFields(**{"expression language": "foo", "labels": {"a": "something", "b": ["x", "y"]}})

    with pytest.raises(ValidationError):
        MappingFields(**{"expression language": "foo", "labels": {"a": "something", "b": 42}})
    with pytest.raises(ValidationError):
        MappingFields(**{"expression language": "foo"})


def test_datapackage_metadata_complete():
    DatapackageMetadata(
        name="Foo",
        description="Bar",
        source_id="Something",
        target_id="Something else",
        homepage="https://example.com",
        created=datetime.datetime.now(),
        version="1.0",
        licenses=[{"foo": "bar"}],
        graph_context=["create", "delete"],
    )


def test_datapackage_metadata_partial():
    DatapackageMetadata(
        name="Foo",
        description="Bar",
        version="1.0",
        licenses=[{"foo": "bar"}],
        graph_context=["create", "delete"],
    )


def test_datapackage_metadata_error():
    with pytest.raises(ValidationError):
        DatapackageMetadata(
            name=42,
            description="Bar",
            source_id="Something",
            target_id="Something else",
            homepage="https://example.com",
            created=datetime.datetime.now(),
            version="1.0",
            licenses=[{"foo": "bar"}],
            graph_context=["create", "delete"],
        )
    with pytest.raises(ValidationError):
        DatapackageMetadata(
            name="Foo",
            description="Bar",
            source_id="Something",
            target_id="Something else",
            homepage="https://example.com",
            created=datetime.datetime.now(),
            version="1.0",
            licenses="foo",
            graph_context=["create", "delete"],
        )
    with pytest.raises(ValidationError):
        DatapackageMetadata(
            description="Bar",
            source_id="Something",
            target_id="Something else",
            homepage="https://example.com",
            created=datetime.datetime.now(),
            version="1.0",
            licenses=[{"foo": "bar"}],
            graph_context=["create", "delete"],
        )


def test_validation_integration():
    Datapackage(
        name="Foo",
        description="Bar",
        contributors=[{"title": "John", "role": "wrangler", "path": "example.com"}],
        mapping_source={
            "expression language": "foo",
            "labels": {"a": "something", "b": ["x", "y"]},
        },
        mapping_target={
            "expression language": "foo",
            "labels": {"a": "something", "b": ["x", "y"]},
        },
        source_id="Something",
        target_id="Something else",
        homepage="https://example.com",
        created=datetime.datetime.now(),
        version="1.0",
        licenses=[{"foo": "bar"}],
        graph_context=["create", "delete"],
    )
    Datapackage(
        name="Foo",
        description="Bar",
        contributors=[{"title": "John", "role": "wrangler", "path": "example.com"}],
        mapping_source={
            "expression language": "foo",
            "labels": {"a": "something", "b": ["x", "y"]},
        },
        mapping_target={
            "expression language": "foo",
            "labels": {"a": "something", "b": ["x", "y"]},
        },
    )
    with pytest.raises(ValidationError):
        Datapackage(
            name=42,
            description="Bar",
            contributors=[{"title": "John", "role": "wrangler", "path": "example.com"}],
            mapping_source={
                "expression language": "foo",
                "labels": {"a": "something", "b": ["x", "y"]},
            },
            mapping_target={
                "expression language": "foo",
                "labels": {"a": "something", "b": ["x", "y"]},
            },
            source_id="Something",
            target_id="Something else",
            homepage="https://example.com",
            created=datetime.datetime.now(),
            version="1.0",
            licenses=[{"foo": "bar"}],
            graph_context=["create", "delete"],
        )
    with pytest.raises(ValidationError):
        Datapackage(
            name="Foo",
            description="Bar",
            contributors=[{"title": "John", "role": "wrangler", "path": "example.com"}],
            mapping_source={"labels": {"a": "something", "b": ["x", "y"]}},
            mapping_target={
                "expression language": "foo",
                "labels": {"a": "something", "b": ["x", "y"]},
            },
            source_id="Something",
            target_id="Something else",
            homepage="https://example.com",
            created=datetime.datetime.now(),
            version="1.0",
            licenses=[{"foo": "bar"}],
            graph_context=["create", "delete"],
        )
    with pytest.raises(ValidationError):
        Datapackage(
            name="Foo",
            description="Bar",
            contributors=[{"title": "John", "role": "wrangler"}],
            mapping_source={
                "expression language": "foo",
                "labels": {"a": "something", "b": ["x", "y"]},
            },
            mapping_target={
                "expression language": "foo",
                "labels": {"a": "something", "b": ["x", "y"]},
            },
            source_id="Something",
            target_id="Something else",
            homepage="https://example.com",
            created=datetime.datetime.now(),
            version="1.0",
            licenses=[{"foo": "bar"}],
            graph_context=["create", "delete"],
        )
