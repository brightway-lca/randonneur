import pytest

from randonneur import MigrationConfig, migrate_nodes


@pytest.fixture
def generic():
    return [
        {
            "name": "n1",
            "reference product": "rp1",
            "location": "l1",
            "unit": "u1",
            "foo": "bar",
        },
        {
            "name": "hey",
            "product": "everybody",
            "unit": "look at",
            "location": "me!",
        },
    ]


@pytest.fixture
def deletion():
    return {
        "delete": [
            {
                "source": {
                    "name": "hey",
                },
            },
        ]
    }


def test_migrate_nodes_delete_simple(generic, deletion):
    assert len(generic) == 2
    migrate_nodes(
        generic,
        deletion,
        MigrationConfig(verbs=["delete"]),
    )
    assert len(generic) == 1
    assert generic[0]["name"] == "n1"


def test_migrate_nodes_delete_multiple_times(generic, deletion):
    assert len(generic) == 2
    migrate_nodes(
        generic,
        deletion,
        MigrationConfig(verbs=["delete"]),
    )
    assert len(generic) == 1
    migrate_nodes(
        generic,
        deletion,
        MigrationConfig(verbs=["delete"]),
    )
    assert len(generic) == 1


def test_migrate_nodes_node_filter(generic, deletion):
    assert len(generic) == 2
    migrate_nodes(
        generic,
        deletion,
        MigrationConfig(node_filter=lambda x: x.get("never work") is True, verbs=["delete"]),
    )
    assert len(generic) == 2
    migrate_nodes(
        generic,
        deletion,
        MigrationConfig(node_filter=lambda x: x["name"] == "hey", verbs=["delete"]),
    )
    assert len(generic) == 1


def test_migrate_nodes_delete_empty(generic):
    assert len(generic) == 2
    migrate_nodes(generic, {"delete": []}, MigrationConfig(verbs=["delete"]))
    assert len(generic) == 2


def test_migrate_nodes_delete_missing(generic):
    assert len(generic) == 2
    migrate_nodes(generic, {}, MigrationConfig(verbs=["delete"]))
    assert len(generic) == 2


def test_migrate_nodes_delete_multiple_identical(generic):
    assert len(generic) == 2
    change = {
        "delete": [
            {
                "source": {
                    "name": "hey",
                },
            },
            {
                "source": {
                    "name": "hey",
                },
            },
        ]
    }
    migrate_nodes(generic, change, MigrationConfig(verbs=["delete"]))
    assert len(generic) == 1


def test_migrate_nodes_multiple_out_of_order():
    data = [
        {"name": "1"},
        {"name": "2"},
        {"name": "3"},
        {"name": "4"},
        {"name": "5"},
        {"name": "6"},
    ]
    change = {
        "delete": [
            {"source": {"name": "5"}},
            {"source": {"name": "3"}},
            {"source": {"name": "1"}},
        ]
    }
    migrate_nodes(data, change, MigrationConfig(verbs=["delete"]))
    assert data == [
        {"name": "2"},
        {"name": "4"},
        {"name": "6"},
    ]
