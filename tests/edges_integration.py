import pytest

from randonneur import migrate_edges


@pytest.fixture
def generic():
    return [
        {
            "name": "n",
            "reference product": "rp",
            "unit": "u",
            "location": "l",
            "edges": [
                {"name": "babur"},
                {
                    "name": "akbar",
                    "amount": 10,
                },
                {
                    "name": "shah jahan",
                    "amount": 10,
                },
                {
                    "name": "azam shah",
                    "amount": 100,
                },
            ],
        }
    ]


@pytest.fixture
def migrate_all():
    return {
        # "delete": [{"name": "babur"}],
        # "create-exchanges": [
        #     {
        #         "dataset": {"name": "n"},
        #         "source": {"name": "humayun"},
        #     }
        # ],
        "replace": [
            {
                "source": {"name": "akbar"},
                "target": {"name": "jahangir", "allocation": 0.5},
            }
        ],
        "update": [
            {
                "source": {"name": "shah jahan"},
                "target": {"name": "alamgir"},
            }
        ],
        "disaggregate": [
            {
                "source": {"name": "azam shah"},
                "targets": [
                    {"name": "bahadur shah", "allocation": 0.25},
                    {"name": "jahandar shah", "allocation": 0.75},
                ],
            }
        ],
    }


def test_migrate_exchanges_integration(generic, migrate_all):
    expected = [
        {
            "name": "n",
            "reference product": "rp",
            "unit": "u",
            "location": "l",
            "edges": [
                {
                    "name": "alamgir",
                    "amount": 10,
                },
                {"name": "humayun"},
                {
                    "name": "jahangir",
                    "amount": 5,
                },
                {
                    "name": "bahadur shah",
                    "amount": 25.,
                    'allocation': 0.25,
                },
                {
                    "name": "jahandar shah",
                    "amount": 75.,
                    'allocation': 0.75,
                },
            ],
        }
    ]
    result = migrate_edges(graph=generic, migrations=migrate_all)
    assert result == expected
