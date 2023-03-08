# pylint: disable-msg-cat=WCREFI
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
