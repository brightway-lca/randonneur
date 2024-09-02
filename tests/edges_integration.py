import pytest

from randonneur import migrate_edges, MigrationConfig


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
                {"name": "akbar", "amount": 10, "foo": {"bar": True}},
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


def test_migrate_edges_integration(generic, migrate_all):
    expected = [
        {
            "name": "n",
            "reference product": "rp",
            "unit": "u",
            "location": "l",
            "edges": [
                {"name": "babur"},
                {"allocation": 0.5, "amount": 5.0, "name": "jahangir", "foo": {"bar": True}},
                {"name": "alamgir", "amount": 10},
                {
                    "name": "bahadur shah",
                    "amount": 25.0,
                    "allocation": 0.25,
                },
                {
                    "name": "jahandar shah",
                    "amount": 75.0,
                    "allocation": 0.75,
                },
            ],
        }
    ]
    result = migrate_edges(graph=generic, migrations=migrate_all)
    assert result == expected


def test_migrate_edges_extra_attrs(generic):
    migration_data = {
        "replace": [
            {
                "source": {"name": "akbar"},
                "target": {"name": "jahangir", "allocation": 0.5},
                "extra": True,
            }
        ],
        "update": [
            {
                "source": {"name": "shah jahan"},
                "target": {"name": "alamgir"},
                "location": "here",
            }
        ],
        "disaggregate": [
            {
                "source": {"name": "azam shah"},
                "targets": [
                    {"name": "bahadur shah", "allocation": 0.25},
                    {"name": "jahandar shah", "allocation": 0.75},
                ],
                "this": "that",
            }
        ],
    }
    expected = [
        {
            "name": "n",
            "reference product": "rp",
            "unit": "u",
            "location": "l",
            "edges": [
                {"name": "babur"},
                {
                    "allocation": 0.5,
                    "amount": 5.0,
                    "name": "jahangir",
                    "foo": {"bar": True},
                    "extra": True,
                },
                {"name": "alamgir", "amount": 10, "location": "here"},
                {"name": "bahadur shah", "amount": 25.0, "allocation": 0.25, "this": "that"},
                {"name": "jahandar shah", "amount": 75.0, "allocation": 0.75, "this": "that"},
            ],
        }
    ]
    result = migrate_edges(
        graph=generic, migrations=migration_data, config=MigrationConfig(add_extra_attributes=True)
    )
    assert result == expected
