import pytest

from randonneur import MigrationConfig, migrate_edges


@pytest.fixture
def generic():
    return [
        {
            "name": "n1",
            "reference product": "rp1",
            "location": "l1",
            "unit": "u1",
            "foo": "bar",
            "edges": [
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
def creation_one():
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


@pytest.fixture
def creation_two():
    return {
        "create": [
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


def test_migrate_edges_create_simple(generic, creation_one, creation_two):
    assert len(generic[0]["edges"]) == 2
    migrate_edges(
        generic,
        creation_one,
        MigrationConfig(edge_filter=lambda x: x["name"] == "hey", verbs=["create"]),
    )
    assert len(generic[0]["edges"]) == 3
    migrate_edges(
        generic,
        creation_two,
        MigrationConfig(node_filter=lambda x: x["name"] == "n1", verbs=["create"]),
    )
    assert len(generic[0]["edges"]) == 4


def test_migrate_edges_edge_filter_not_apply(generic, creation_one):
    assert len(generic[0]["edges"]) == 2
    migrate_edges(
        generic,
        creation_one,
        MigrationConfig(edge_filter=lambda x: x["location"] == "over there", verbs=["create"]),
    )
    assert len(generic[0]["edges"]) == 3


def test_migrate_edges_create_empty(generic):
    assert len(generic[0]["edges"]) == 2
    migrate_edges(generic, {"create": []}, MigrationConfig(verbs=["create"]))
    assert len(generic[0]["edges"]) == 2


def test_migrate_edges_create_missing(generic):
    assert len(generic[0]["edges"]) == 2
    migrate_edges(generic, {}, MigrationConfig(verbs=["create"]))
    assert len(generic[0]["edges"]) == 2


def test_migrate_edges_create_multiple_identical(generic):
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
    assert len(generic[0]["edges"]) == 2
    migrate_edges(generic, change, MigrationConfig(verbs=["create"]))
    assert len(generic[0]["edges"]) == 4


def test_migrate_edges_warnings(creation_one, creation_two, recwarn):
    from randonneur.edge_functions import warning_semaphore

    warning_semaphore.missing_edges_label = False

    assert len(recwarn) == 0
    migrate_edges(
        [{"name": "foo"}],
        creation_one,
        MigrationConfig(verbs=["create"]),
    )
    assert len(recwarn) == 1
    migrate_edges(
        [{"name": "foo"}],
        creation_two,
        MigrationConfig(verbs=["create"]),
    )
    assert len(recwarn) == 1
