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
def deletion_one():
    return {
        "delete": [
            {
                "source": {
                    "name": "n1",
                    "product": "rp1",
                    "unit": "u1",
                    "location": "l1",
                },
            },
        ]
    }


@pytest.fixture
def deletion_two():
    return {
        "delete": [
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


def test_migrate_edges_delete_simple(generic, deletion_one, deletion_two):
    assert len(generic[0]["edges"]) == 2
    migrate_edges(
        generic,
        deletion_one,
        MigrationConfig(edge_filter=lambda x: x["name"] == "n1", verbs=["delete"]),
    )
    assert len(generic[0]["edges"]) == 1
    migrate_edges(
        generic,
        deletion_two,
        MigrationConfig(node_filter=lambda x: x["location"] == "l1", verbs=["delete"]),
    )
    assert len(generic[0]["edges"]) == 0


def test_migrate_edges_delete_empty(generic):
    assert len(generic[0]["edges"]) == 2
    migrate_edges(
        generic,
        {"delete": []},
        MigrationConfig(verbs=["delete"]),
    )
    assert len(generic[0]["edges"]) == 2


def test_migrate_edges_delete_missing(generic):
    assert len(generic[0]["edges"]) == 2
    migrate_edges(
        generic,
        {},
        MigrationConfig(verbs=["delete"]),
    )
    assert len(generic[0]["edges"]) == 2


def test_migrate_edges_edge_filter_fail(generic, deletion_one):
    assert len(generic[0]["edges"]) == 2
    migrate_edges(
        generic,
        deletion_one,
        MigrationConfig(edge_filter=lambda x: x["name"] == "not this one", verbs=["delete"]),
    )
    assert len(generic[0]["edges"]) == 2


def test_migrate_edges_delete_multiple_identical(deletion_one):
    database = [
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
                    "amount": 1,
                    "name": "n1",
                    "product": "rp1",
                    "unit": "u1",
                    "location": "l1",
                },
            ],
        }
    ]
    assert len(database[0]["edges"]) == 2
    migrate_edges(
        database,
        deletion_one,
        MigrationConfig(verbs=["delete"]),
    )
    assert len(database[0]["edges"]) == 0


def test_migrate_edges_delete_warnings(deletion_one, deletion_two, recwarn):
    from randonneur.edge_functions import warning_semaphore

    warning_semaphore.missing_edges_label = False

    assert len(recwarn) == 0
    migrate_edges(
        [{"name": "foo"}],
        deletion_one,
        MigrationConfig(verbs=["delete"]),
    )
    assert len(recwarn) == 1
    migrate_edges(
        [{"name": "foo"}],
        deletion_two,
        MigrationConfig(verbs=["delete"]),
    )
    assert len(recwarn) == 1
