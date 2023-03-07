from bw_migrate import migrate_exchanges
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
                "target": {
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
                "target": {
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
        deletion, generic, create=False, disaggregate=False, replace=False, update=False, verbose=True
    )
    assert not result[0]["exchanges"]


def test_migrate_exchanges_delete_simple(generic, deletion):
    result = migrate_exchanges(
        deletion, generic, create=False, disaggregate=False, replace=False, update=False
    )
    assert not result[0]["exchanges"]


def test_migrate_exchanges_delete_node_filter(generic, deletion):
    result = migrate_exchanges(
        deletion, copy(generic), create=False, disaggregate=False, replace=False, update=False, node_filter=lambda x: x['name'] == 'n2'
    )
    assert len(result[0]["exchanges"]) == 2
    result = migrate_exchanges(
        deletion, copy(generic), create=False, disaggregate=False, replace=False, update=False, node_filter=lambda x: x['name'] == 'n1'
    )
    assert not result[0]["exchanges"]
