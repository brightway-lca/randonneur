import datetime

import pytest
from pydantic import ValidationError

from randonneur import Datapackage
from randonneur.validation import Contributor, DatapackageMetadata, MappingFields


def test_contributors():
    Contributor(**{"title": "John", "roles": ["wrangler"], "path": "example.com"})
    Contributor(**{"title": "John", "roles": ["creator"], "path": "example.com", "extra": "ignore"})

    with pytest.raises(ValidationError):
        Contributor(**{"title": "John", "roles": ["wrangler"]})  # Missing `path`


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
        contributors=[{"title": "John", "roles": ["wrangler"], "path": "example.com"}],
    )


def test_datapackage_metadata_partial():
    DatapackageMetadata(
        name="Foo",
        description="Bar",
        version="1.0",
        licenses=[{"foo": "bar"}],
        graph_context=["create", "delete"],
        contributors=[{"title": "John", "roles": ["wrangler"], "path": "example.com"}],
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
            contributors=[{"title": "John", "roles": ["wrangler"], "path": "example.com"}],
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
            contributors=[{"title": "John", "roles": ["wrangler"], "path": "example.com"}],
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
            contributors=[{"title": "John", "roles": ["wrangler"], "path": "example.com"}],
        )


def test_validation_integration():
    Datapackage(
        name="Foo",
        description="Bar",
        contributors=[{"title": "John", "roles": ["wrangler"], "path": "example.com"}],
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
        contributors=[{"title": "John", "roles": ["wrangler"], "path": "example.com"}],
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
            contributors=[{"title": "John", "roles": ["wrangler"], "path": "example.com"}],
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
            contributors=[{"title": "John", "roles": ["wrangler"], "path": "example.com"}],
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
            contributors=[{"title": "John", "roles": ["wrangler"]}],
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
