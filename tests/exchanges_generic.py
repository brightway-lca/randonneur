# pylint: disable-msg-cat=WCREFI
import pytest

from randonneur import migrate_exchanges
from randonneur.exchanges import as_tuple


@pytest.fixture
def generic():
    return [
        {
            "name": "n1",
            "reference product": "rp1",
            "location": "l1",
            "unit": "u1",
            "foo": "bar",
            "exchanges": [
                {
                    "amount": 1,
                    "name": "n1",
                    "product": "rp1",
                    "unit": "u1",
                    "location": "l1",
                    "extra": "yes please",
                },
                {
                    "amount": 42,
                    "name": "n2",
                    "product": "rp1",
                    "unit": "u1",
                    "location": "l2",
                    "extra": "yes please",
                },
            ],
        }
    ]


@pytest.fixture
def deletion():
    return {
        "delete": [
            {
                "source": {
                    "name": "n1",
                    "product": "rp1",
                    "unit": "u1",
                    "location": "l1",
                },
                "node": {
                    "name": "n1",
                    "reference product": "rp1",
                    "location": "l1",
                    "unit": "u1",
                },
            },
            {
                "source": {
                    "name": "n2",
                    "product": "rp1",
                    "unit": "u1",
                    "location": "l2",
                    "extra": "yes please",
                },
            },
        ]
    }


def test_migrate_exchanges_empty_migration(generic):
    assert migrate_exchanges({}, generic)


def test_migrate_exchanges_verbose(generic, deletion):
    result = migrate_exchanges(
        deletion,
        generic,
        verbose=True,
    )
    assert not result[0]["exchanges"]


# TBD
def test_unhashable_data():
    pass


def test_as_tuple_convert_list():
    given = {"foo": "bar", "this": ["that", "other thing"]}
    fields = ("foo", "this")
    assert as_tuple(given, fields) == ("bar", ("that", "other thing"))


def test_as_tuple_str_tuple_set():
    given = {"foo": "bar", "this": ("that", "other thing"), "weee": {1, 2, 3}}
    fields = ("foo", "this", "weee")
    assert as_tuple(given, fields) == ("bar", ("that", "other thing"), {1, 2, 3})


def test_as_tuple_none_for_missing_fields():
    given = {"foo": "bar", "this": ("that", "other thing")}
    fields = ("foo", "this", "weee")
    assert as_tuple(given, fields) == ("bar", ("that", "other thing"), None)


def test_as_tuple_only_given_fields():
    given = {"foo": "bar", "this": ("that", "other thing"), "weee": {1, 2, 3}}
    fields = ("foo", "this")
    assert as_tuple(given, fields) == ("bar", ("that", "other thing"))


def test_as_tuple_not_sort_fields():
    given = {"foo": "bar", "this": ("that", "other thing")}
    fields = ("this", "foo")
    assert as_tuple(given, fields) == (("that", "other thing"), "bar")
