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
        }
    ]


@pytest.fixture
def creation():
    return {
        "create": [
            {
                "target": {
                    "name": "hey",
                    "product": "everybody",
                    "unit": "look at",
                    "location": "me!",
                },
            },
        ]
    }


def test_migrate_nodes_create_simple(generic, creation):
    assert len(generic) == 1
    migrate_nodes(
        generic,
        creation,
        MigrationConfig(verbs=["create"]),
    )
    assert len(generic) == 2
    assert generic[1]["name"] == "hey"


def test_migrate_nodes_create_multiple_times(generic, creation):
    assert len(generic) == 1
    migrate_nodes(
        generic,
        creation,
        MigrationConfig(verbs=["create"]),
    )
    assert len(generic) == 2
    migrate_nodes(
        generic,
        creation,
        MigrationConfig(verbs=["create"]),
    )
    assert len(generic) == 3
    assert generic[1] == generic[2]


def test_migrate_nodes_node_filter_not_apply(generic, creation):
    assert len(generic) == 1
    migrate_nodes(
        generic,
        creation,
        MigrationConfig(node_filter=lambda x: x["location"] == "over there", verbs=["create"]),
    )
    assert len(generic) == 2


def test_migrate_nodes_create_empty(generic):
    assert len(generic) == 1
    migrate_nodes(generic, {"create": []}, MigrationConfig(verbs=["create"]))
    assert len(generic) == 1


def test_migrate_nodes_create_missing(generic):
    assert len(generic) == 1
    migrate_nodes(generic, {}, MigrationConfig(verbs=["create"]))
    assert len(generic) == 1


def test_migrate_nodes_create_multiple_identical(generic):
    assert len(generic) == 1
    change = {
        "create": [
            {
                "target": {
                    "name": "1001",
                    "product": "1002",
                    "unit": "1003",
                    "location": "1004",
                },
            },
            {
                "target": {
                    "name": "1001",
                    "product": "1002",
                    "unit": "1003",
                    "location": "1004",
                },
            },
        ]
    }
    migrate_nodes(generic, change, MigrationConfig(verbs=["create"]))
    assert len(generic) == 3
