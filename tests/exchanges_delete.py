# pylint: disable-msg-cat=WCREFI
from copy import copy

import pytest

from randonneur import migrate_exchanges


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


def test_migrate_exchanges_delete_simple(generic, deletion):
    result = migrate_exchanges(
        deletion, generic, create=False, disaggregate=False, replace=False, update=False
    )
    assert not result[0]["exchanges"]


def test_migrate_exchanges_delete_empty(generic, deletion):
    result = migrate_exchanges(
        {"delete": []},
        generic,
    )
    assert len(result[0]["exchanges"]) == 2


def test_migrate_exchanges_delete_missing(generic, deletion):
    result = migrate_exchanges(
        {}, generic, create=False, disaggregate=False, replace=False, update=False
    )
    assert len(result[0]["exchanges"]) == 2


def test_migrate_exchanges_delete_node_filter(generic, deletion):
    result = migrate_exchanges(
        deletion,
        copy(generic),
        node_filter=lambda x: x["name"] == "n2",
    )
    assert len(result[0]["exchanges"]) == 2
    result = migrate_exchanges(
        deletion,
        copy(generic),
        node_filter=lambda x: x["name"] == "n1",
    )
    assert not result[0]["exchanges"]


def test_migrate_exchanges_delete_exchange_filter(generic, deletion):
    result = migrate_exchanges(
        deletion,
        copy(generic),
        exchange_filter=lambda x: x["name"] == "n1",
    )
    assert len(result[0]["exchanges"]) == 1
    result = migrate_exchanges(
        deletion,
        copy(generic),
        exchange_filter=lambda x: x["name"] == "n2",
    )
    assert not result[0]["exchanges"]


def test_migrate_exchanges_delete_custom_fields(generic, deletion):
    assert len(generic[0]["exchanges"]) == 2
    result = migrate_exchanges(
        deletion, copy(generic), fields=("name", "location", "extra")
    )
    assert len(result[0]["exchanges"]) == 1


def test_migrate_exchanges_delete_custom_fields_match_missing(generic, deletion):
    assert len(generic[0]["exchanges"]) == 2
    result = migrate_exchanges(
        deletion, copy(generic), fields=("name", "location", "missing")
    )
    assert len(result[0]["exchanges"]) == 0
