import datetime

import pytest
from pydantic import ValidationError

from randonneur import Datapackage
from randonneur.errors import UnmappedData
from randonneur.validation import Contributor, DatapackageMetadata, MappingFields, validate_data_for_verb


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


# Test fixtures for validate_data_for_verb
@pytest.fixture
def sample_mapping():
    """Sample mapping with source and target labels"""
    return {
        "source": {
            "expression language": "JSONPath",
            "labels": {
                "name": "Node.name",
                "location": "Node.location",
                "unit": "Node.unit",
            },
        },
        "target": {
            "expression language": "JSONPath",
            "labels": {
                "name": "Node.name",
                "product": "Node.product",
                "location": "Node.location",
                "unit": "Node.unit",
            },
        },
    }


# Test cases for validate_data_for_verb - CREATE verb
def test_validate_data_for_verb_create_valid(sample_mapping):
    """Test valid create verb with all target keys in mapping"""
    data = [
        {
            "target": {
                "name": "hey",
                "product": "everybody",
                "unit": "look at",
                "location": "me!",
            },
        },
    ]
    # Should not raise any exception
    validate_data_for_verb("create", data, sample_mapping)


def test_validate_data_for_verb_create_with_allocation(sample_mapping):
    """Test create verb with allocation field (allowed special field)"""
    data = [
        {
            "target": {
                "name": "hey",
                "product": "everybody",
                "unit": "look at",
                "location": "me!",
                "allocation": 0.5,
            },
        },
    ]
    # Should not raise any exception
    validate_data_for_verb("create", data, sample_mapping)


def test_validate_data_for_verb_create_invalid_target_key(sample_mapping):
    """Test create verb with unmapped target key"""
    data = [
        {
            "target": {
                "name": "hey",
                "product": "everybody",
                "unit": "look at",
                "location": "me!",
                "invalid_key": "value",
            },
        },
    ]
    with pytest.raises(UnmappedData):
        validate_data_for_verb("create", data, sample_mapping)


# Test cases for validate_data_for_verb - REPLACE verb
def test_validate_data_for_verb_replace_valid(sample_mapping):
    """Test valid replace verb with all source and target keys in mapping"""
    data = [
        {
            "source": {"name": "akbar"},
            "target": {"name": "jahangir", "location": "l1", "unit": "u1", "product": "p1"},
        },
    ]
    # Should not raise any exception
    validate_data_for_verb("replace", data, sample_mapping)


def test_validate_data_for_verb_replace_with_allocation(sample_mapping):
    """Test replace verb with allocation field (allowed special field)"""
    data = [
        {
            "source": {"name": "akbar"},
            "target": {"name": "jahangir", "allocation": 0.5},
        },
    ]
    # Should not raise any exception
    validate_data_for_verb("replace", data, sample_mapping)


def test_validate_data_for_verb_replace_invalid_source_key(sample_mapping):
    """Test replace verb with unmapped source key"""
    data = [
        {
            "source": {"name": "akbar", "invalid_source": "value"},
            "target": {"name": "jahangir"},
        },
    ]
    with pytest.raises(UnmappedData):
        validate_data_for_verb("replace", data, sample_mapping)


def test_validate_data_for_verb_replace_invalid_target_key(sample_mapping):
    """Test replace verb with unmapped target key"""
    data = [
        {
            "source": {"name": "akbar"},
            "target": {"name": "jahangir", "invalid_target": "value"},
        },
    ]
    with pytest.raises(UnmappedData):
        validate_data_for_verb("replace", data, sample_mapping)


# Test cases for validate_data_for_verb - UPDATE verb
def test_validate_data_for_verb_update_valid(sample_mapping):
    """Test valid update verb with all source and target keys in mapping"""
    data = [
        {
            "source": {"name": "shah jahan"},
            "target": {"name": "alamgir", "location": "l2"},
        },
    ]
    # Should not raise any exception
    validate_data_for_verb("update", data, sample_mapping)


def test_validate_data_for_verb_update_with_allocation(sample_mapping):
    """Test update verb with allocation field (allowed special field)"""
    data = [
        {
            "source": {"name": "shah jahan"},
            "target": {"name": "alamgir", "allocation": 0.75},
        },
    ]
    # Should not raise any exception
    validate_data_for_verb("update", data, sample_mapping)


def test_validate_data_for_verb_update_invalid_source_key(sample_mapping):
    """Test update verb with unmapped source key"""
    data = [
        {
            "source": {"name": "shah jahan", "unknown_field": "value"},
            "target": {"name": "alamgir"},
        },
    ]
    with pytest.raises(UnmappedData):
        validate_data_for_verb("update", data, sample_mapping)


def test_validate_data_for_verb_update_invalid_target_key(sample_mapping):
    """Test update verb with unmapped target key"""
    data = [
        {
            "source": {"name": "shah jahan"},
            "target": {"name": "alamgir", "unknown_field": "value"},
        },
    ]
    with pytest.raises(UnmappedData):
        validate_data_for_verb("update", data, sample_mapping)


# Test cases for validate_data_for_verb - DELETE verb
def test_validate_data_for_verb_delete_valid(sample_mapping):
    """Test valid delete verb with all source keys in mapping"""
    data = [
        {
            "source": {"name": "hey"},
        },
    ]
    # Should not raise any exception
    validate_data_for_verb("delete", data, sample_mapping)


def test_validate_data_for_verb_delete_multiple_fields(sample_mapping):
    """Test delete verb with multiple source fields"""
    data = [
        {
            "source": {"name": "n1", "location": "l1", "unit": "u1"},
        },
    ]
    # Should not raise any exception
    validate_data_for_verb("delete", data, sample_mapping)


def test_validate_data_for_verb_delete_invalid_source_key(sample_mapping):
    """Test delete verb with unmapped source key"""
    data = [
        {
            "source": {"name": "hey", "invalid_key": "value"},
        },
    ]
    with pytest.raises(UnmappedData):
        validate_data_for_verb("delete", data, sample_mapping)


# Test cases for validate_data_for_verb - DISAGGREGATE verb
def test_validate_data_for_verb_disaggregate_valid(sample_mapping):
    """Test valid disaggregate verb with all source and target keys in mapping"""
    data = [
        {
            "source": {"name": "azam shah"},
            "targets": [
                {"name": "bahadur shah", "location": "l1"},
                {"name": "jahandar shah", "location": "l2"},
            ],
        },
    ]
    # Should not raise any exception
    validate_data_for_verb("disaggregate", data, sample_mapping)


def test_validate_data_for_verb_disaggregate_with_allocation(sample_mapping):
    """Test disaggregate verb with allocation field (allowed special field)"""
    data = [
        {
            "source": {"name": "azam shah"},
            "targets": [
                {"name": "bahadur shah", "allocation": 0.25},
                {"name": "jahandar shah", "allocation": 0.75},
            ],
        },
    ]
    # Should not raise any exception
    validate_data_for_verb("disaggregate", data, sample_mapping)


def test_validate_data_for_verb_disaggregate_invalid_source_key(sample_mapping):
    """Test disaggregate verb with unmapped source key"""
    data = [
        {
            "source": {"name": "azam shah", "invalid_source": "value"},
            "targets": [
                {"name": "bahadur shah"},
            ],
        },
    ]
    with pytest.raises(UnmappedData):
        validate_data_for_verb("disaggregate", data, sample_mapping)


def test_validate_data_for_verb_disaggregate_invalid_target_key(sample_mapping):
    """Test disaggregate verb with unmapped target key in targets list"""
    data = [
        {
            "source": {"name": "azam shah"},
            "targets": [
                {"name": "bahadur shah", "invalid_target": "value"},
            ],
        },
    ]
    with pytest.raises(UnmappedData):
        validate_data_for_verb("disaggregate", data, sample_mapping)


def test_validate_data_for_verb_disaggregate_multiple_targets_with_invalid(sample_mapping):
    """Test disaggregate verb with one target having invalid key"""
    data = [
        {
            "source": {"name": "azam shah"},
            "targets": [
                {"name": "bahadur shah", "location": "l1"},
                {"name": "jahandar shah", "invalid_field": "value"},
            ],
        },
    ]
    with pytest.raises(UnmappedData):
        validate_data_for_verb("disaggregate", data, sample_mapping)


# Test cases for invalid verb
def test_validate_data_for_verb_invalid_verb(sample_mapping):
    """Test validate_data_for_verb with invalid verb"""
    data = [{"target": {"name": "test"}}]
    with pytest.raises(ValueError, match="Transformation verb invalid_verb must be one of"):
        validate_data_for_verb("invalid_verb", data, sample_mapping)


# Test cases with multiple data elements
def test_validate_data_for_verb_multiple_elements_all_valid(sample_mapping):
    """Test validate_data_for_verb with multiple valid elements"""
    data = [
        {
            "target": {
                "name": "hey",
                "product": "everybody",
                "unit": "look at",
                "location": "me!",
            },
        },
        {
            "target": {
                "name": "test2",
                "product": "p2",
                "unit": "u2",
                "location": "l2",
            },
        },
    ]
    # Should not raise any exception
    validate_data_for_verb("create", data, sample_mapping)


def test_validate_data_for_verb_multiple_elements_one_invalid(sample_mapping):
    """Test validate_data_for_verb with multiple elements, one invalid"""
    data = [
        {
            "target": {
                "name": "hey",
                "product": "everybody",
                "unit": "look at",
                "location": "me!",
            },
        },
        {
            "target": {
                "name": "test2",
                "product": "p2",
                "unit": "u2",
                "location": "l2",
                "invalid_field": "value",
            },
        },
    ]
    with pytest.raises(UnmappedData):
        validate_data_for_verb("create", data, sample_mapping)
