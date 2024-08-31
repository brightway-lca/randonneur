import pytest

from randonneur.errors import MultipleTransformations, ConflictingConversionFactors
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
    assert fld[{"foo": "b", "other": "whatever"}] == {"source": {"foo": "b"}}
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


def test_flexible_lookup_dict_similar_allowed():
    FlexibleLookupDict(
        input_data=[
            {"source": {"foo": "a", "bar": "b"}, "target": {"foo": "strawberry"}},
            {"source": {"foo": "a"}, "target": {"foo": "strawberry"}},
        ],
        fields_filter=["foo"],
        case_sensitive=False,
    )


def test_flexible_lookup_dict_multiple_transformations():
    with pytest.raises(MultipleTransformations):
        FlexibleLookupDict(
            input_data=[
                {"source": {"foo": "a", "bar": "b"}, "target": {"foo": "strawberry"}},
                {"source": {"foo": "a"}, "target": {"foo": "raspberry"}},
            ],
            fields_filter=["foo"],
            case_sensitive=False,
        )


def test_flexible_lookup_dict_multiple_transformations_disaggregation():
    with pytest.raises(MultipleTransformations):
        FlexibleLookupDict(
            input_data=[
                {"source": {"foo": "a", "bar": "b"}, "targets": {}},
                {"source": {"foo": "a"}, "targets": {}},
            ],
            fields_filter=["foo"],
            case_sensitive=False,
        )


def test_flexible_lookup_dict_conflicting_conversions():
    with pytest.raises(ConflictingConversionFactors):
        FlexibleLookupDict(
            input_data=[
                {
                    "source": {"foo": "a", "bar": "b"},
                    "target": {"foo": "banana"},
                    "conversion_factor": 1000,
                },
                {
                    "source": {"foo": "a", "bar": "b"},
                    "target": {"foo": "banana"},
                    "conversion_factor": 0.001,
                },
            ],
        )


def test_flexible_lookup_dict_no_conflicting_conversions():
    FlexibleLookupDict(
        input_data=[
            {
                "source": {"foo": "a", "bar": "b"},
                "target": {"foo": "banana"},
                "conversion_factor": 1,
            },
            {
                "source": {"foo": "a", "bar": "b"},
                "target": {"foo": "banana"},
                "conversion_factor": 0.995,
            },
        ],
    )


def test_flexible_lookup_dict_conversions_take_later_value():
    result = FlexibleLookupDict(
        input_data=[
            {
                "source": {"foo": "a", "bar": "b"},
                "target": {"foo": "banana"},
            },
            {
                "source": {"foo": "a", "bar": "b"},
                "target": {"foo": "banana"},
                "conversion_factor": 0.995,
            },
        ],
        fields_filter=["foo"],
    )
    assert result[{"foo": "a"}] == {
        "source": {"foo": "a", "bar": "b"},
        "target": {"foo": "banana"},
        "conversion_factor": 0.995,
    }
