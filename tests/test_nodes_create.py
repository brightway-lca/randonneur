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


def test_migrate_nodes_create_empty_graph(creation):
    """Test create with empty graph"""
    graph = []
    result = migrate_nodes(graph, creation, MigrationConfig(verbs=["create"]))
    assert len(graph) == 1
    assert graph[0]["name"] == "hey"
    assert result is graph


def test_migrate_nodes_create_return_value(generic, creation):
    """Test that migrate_nodes returns the graph"""
    result = migrate_nodes(generic, creation, MigrationConfig(verbs=["create"]))
    assert result is generic
    assert len(result) == 2


def test_migrate_nodes_create_deep_copy(generic):
    """Test that created nodes are deep copies and don't affect original migration data"""
    creation_data = {
        "create": [
            {
                "target": {
                    "name": "new_node",
                    "value": 42,
                },
            },
        ]
    }
    original_creation = creation_data.copy()
    result = migrate_nodes(generic, creation_data, MigrationConfig(verbs=["create"]))
    
    # Modify the created node
    generic[1]["value"] = 100
    
    # Original migration data should not be affected
    assert creation_data == original_creation
    assert creation_data["create"][0]["target"]["value"] == 42
    # But the node in graph should be modified
    assert generic[1]["value"] == 100


def test_migrate_nodes_create_multiple_nodes(generic):
    """Test creating multiple different nodes"""
    creation_data = {
        "create": [
            {
                "target": {
                    "name": "node1",
                    "location": "loc1",
                },
            },
            {
                "target": {
                    "name": "node2",
                    "location": "loc2",
                },
            },
            {
                "target": {
                    "name": "node3",
                    "location": "loc3",
                },
            },
        ]
    }
    original_length = len(generic)
    result = migrate_nodes(generic, creation_data, MigrationConfig(verbs=["create"]))
    assert len(generic) == original_length + 3
    assert generic[1]["name"] == "node1"
    assert generic[2]["name"] == "node2"
    assert generic[3]["name"] == "node3"
    assert result is generic


def test_migrate_nodes_create_nested_structures(generic):
    """Test creating nodes with nested structures (lists, dicts)"""
    creation_data = {
        "create": [
            {
                "target": {
                    "name": "nested_node",
                    "metadata": {
                        "key1": "value1",
                        "key2": ["a", "b", "c"],
                    },
                    "tags": ["tag1", "tag2"],
                },
            },
        ]
    }
    result = migrate_nodes(generic, creation_data, MigrationConfig(verbs=["create"]))
    assert len(generic) == 2
    assert generic[1]["name"] == "nested_node"
    assert generic[1]["metadata"]["key1"] == "value1"
    assert generic[1]["metadata"]["key2"] == ["a", "b", "c"]
    assert generic[1]["tags"] == ["tag1", "tag2"]
    
    # Modify nested structure to verify deep copy
    generic[1]["metadata"]["key1"] = "modified"
    generic[1]["tags"].append("tag3")
    
    # Original migration data should not be affected
    assert creation_data["create"][0]["target"]["metadata"]["key1"] == "value1"
    assert len(creation_data["create"][0]["target"]["tags"]) == 2
