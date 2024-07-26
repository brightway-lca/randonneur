import pytest

from randonneur.errors import MultipleTransformations
from randonneur.utils import FlexibleLookupDict


def test_flexible_lookup_dict_basic():
    fld = FlexibleLookupDict(
        input_data=[
            {"source": {"foo": "a", "bar": "b"}},
            {"source": {"foo": "b"}},
        ],
        fields_filter=None,
        case_sensitive=True,
    )
    assert fld[{"foo": "b"}] == {"source": {"foo": "b"}}
    assert fld[{"foo": "a", "bar": "b"}] == {"source": {"foo": "a", "bar": "b"}}
    with pytest.raises(KeyError):
        fld[{"foo": "B"}]

    assert {("foo",), ("bar", "foo")} == fld._field_combinations


def test_flexible_lookup_dict_case_insensitive():
    fld = FlexibleLookupDict(
        input_data=[
            {"source": {"foo": "a", "bar": "b"}},
            {"source": {"foo": "b"}},
        ],
        fields_filter=None,
        case_sensitive=False,
    )
    assert fld[{"foo": "b"}] == {"source": {"foo": "b"}}
    assert fld[{"foo": "B"}] == {"source": {"foo": "b"}}
    assert fld[{"foo": "a", "bar": "B"}] == {"source": {"foo": "a", "bar": "b"}}


def test_flexible_lookup_dict_field_filter():
    fld = FlexibleLookupDict(
        input_data=[
            {"source": {"foo": "a", "bar": "b"}},
            {"source": {"foo": "b"}},
        ],
        fields_filter=["foo"],
        case_sensitive=False,
    )
    assert fld[{"foo": "b"}] == {"source": {"foo": "b"}}
    assert fld[{"foo": "B"}] == {"source": {"foo": "b"}}
    assert fld[{"foo": "a", "bar": "B"}] == {"source": {"foo": "a", "bar": "b"}}
    assert fld[{"foo": "a"}] == {"source": {"foo": "a", "bar": "b"}}

    assert {("foo",)} == fld._field_combinations


def test_flexible_lookup_dict_ignore_allocated():
    fld = FlexibleLookupDict(
        input_data=[
            {"source": {"foo": "a", "bar": "b", "allocation": 0.5}},
            {"source": {"foo": "b"}},
        ],
        fields_filter=None,
        case_sensitive=True,
    )
    assert fld[{"foo": "a", "bar": "b"}] == {"source": {"foo": "a", "bar": "b", "allocation": 0.5}}
    assert {("foo",), ("bar", "foo")} == fld._field_combinations


def test_flexible_lookup_dict_multiple_transformations():
    with pytest.raises(MultipleTransformations):
        FlexibleLookupDict(
            input_data=[
                {"source": {"foo": "a", "bar": "b"}},
                {"source": {"foo": "a"}},
            ],
            fields_filter=["foo"],
            case_sensitive=False,
        )
