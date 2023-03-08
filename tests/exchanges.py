from randonneur import migrate_exchanges
from randonneur.exchanges import as_tuple
from copy import copy
import pytest


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
                },
                {
                    "amount": 42,
                    "name": "n2",
                    "product": "rp1",
                    "unit": "u1",
                    "location": "l2",
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
                },
            },
        ]
    }


def test_migrate_exchanges_verbose(generic, deletion):
    result = migrate_exchanges(
        deletion,
        generic,
        create=False,
        disaggregate=False,
        replace=False,
        update=False,
        verbose=True,
    )
    assert not result[0]["exchanges"]


def test_migrate_exchanges_delete_simple(generic, deletion):
    result = migrate_exchanges(
        deletion, generic, create=False, disaggregate=False, replace=False, update=False
    )
    assert not result[0]["exchanges"]


def test_migrate_exchanges_delete_node_filter(generic, deletion):
    result = migrate_exchanges(
        deletion,
        copy(generic),
        create=False,
        disaggregate=False,
        replace=False,
        update=False,
        node_filter=lambda x: x["name"] == "n2",
    )
    assert len(result[0]["exchanges"]) == 2
    result = migrate_exchanges(
        deletion,
        copy(generic),
        create=False,
        disaggregate=False,
        replace=False,
        update=False,
        node_filter=lambda x: x["name"] == "n1",
    )
    assert not result[0]["exchanges"]


def test_migrate_exchanges_delete_exchange_filter(generic, deletion):
    result = migrate_exchanges(
        deletion,
        copy(generic),
        create=False,
        disaggregate=False,
        replace=False,
        update=False,
        exchange_filter=lambda x: x["name"] == "n1",
    )
    assert len(result[0]["exchanges"]) == 1
    result = migrate_exchanges(
        deletion,
        copy(generic),
        create=False,
        disaggregate=False,
        replace=False,
        update=False,
        exchange_filter=lambda x: x["name"] == "n2",
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
