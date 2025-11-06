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
    """Test edge_filter preventing edge creation when filter returns False"""
    assert len(generic[0]["edges"]) == 2
    migrate_edges(
        generic,
        creation_one,
        MigrationConfig(edge_filter=lambda x: x["location"] == "over there", verbs=["create"]),
    )
    # Edge should NOT be added because filter returns False (location is "me!", not "over there")
    assert len(generic[0]["edges"]) == 2


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


def test_migrate_edges_edge_filter_allows_creation(generic, creation_one):
    """Test edge_filter allowing edge creation when filter returns True"""
    assert len(generic[0]["edges"]) == 2
    migrate_edges(
        generic,
        creation_one,
        MigrationConfig(edge_filter=lambda x: x["location"] == "me!", verbs=["create"]),
    )
    # Edge should be added because filter returns True (location is "me!")
    assert len(generic[0]["edges"]) == 3
    assert generic[0]["edges"][2]["name"] == "hey"
    assert generic[0]["edges"][2]["location"] == "me!"


def test_migrate_edges_edge_filter_prevents_creation(generic, creation_one):
    """Test edge_filter preventing edge creation when filter returns False"""
    assert len(generic[0]["edges"]) == 2
    migrate_edges(
        generic,
        creation_one,
        MigrationConfig(edge_filter=lambda x: x.get("name") != "hey", verbs=["create"]),
    )
    # Edge should NOT be added because filter returns False (name is "hey")
    assert len(generic[0]["edges"]) == 2


def test_migrate_edges_edge_filter_multiple_edges_some_filtered(generic):
    """Test edge_filter with multiple edges where some are filtered out"""
    creation_data = {
        "create": [
            {
                "target": {
                    "name": "edge1",
                    "product": "p1",
                    "unit": "u1",
                    "location": "l1",
                },
            },
            {
                "target": {
                    "name": "edge2",
                    "product": "p2",
                    "unit": "u2",
                    "location": "l2",
                },
            },
            {
                "target": {
                    "name": "edge3",
                    "product": "p3",
                    "unit": "u3",
                    "location": "l3",
                },
            },
        ]
    }
    assert len(generic[0]["edges"]) == 2
    # Filter allows only edges with location "l1" or "l3"
    migrate_edges(
        generic,
        creation_data,
        MigrationConfig(
            edge_filter=lambda x: x.get("location") in ["l1", "l3"], verbs=["create"]
        ),
    )
    # Should have 2 original + 2 new edges (edge2 filtered out)
    assert len(generic[0]["edges"]) == 4
    # Verify edge1 and edge3 were added
    names = [edge["name"] for edge in generic[0]["edges"]]
    assert "edge1" in names
    assert "edge3" in names
    assert "edge2" not in names


def test_migrate_edges_edge_filter_multiple_identical_with_filter(generic):
    """Test edge_filter with multiple identical edges"""
    creation_data = {
        "create": [
            {
                "target": {
                    "name": "duplicate",
                    "product": "p1",
                    "unit": "u1",
                    "location": "allowed",
                },
            },
            {
                "target": {
                    "name": "duplicate",
                    "product": "p1",
                    "unit": "u1",
                    "location": "allowed",
                },
            },
            {
                "target": {
                    "name": "duplicate",
                    "product": "p1",
                    "unit": "u1",
                    "location": "filtered",
                },
            },
        ]
    }
    assert len(generic[0]["edges"]) == 2
    # Filter allows only edges with location "allowed"
    migrate_edges(
        generic,
        creation_data,
        MigrationConfig(
            edge_filter=lambda x: x.get("location") == "allowed", verbs=["create"]
        ),
    )
    # Should have 2 original + 2 new edges (one duplicate filtered out)
    assert len(generic[0]["edges"]) == 4
    # Verify only "allowed" location edges were added
    locations = [edge["location"] for edge in generic[0]["edges"]]
    assert locations.count("allowed") == 2
    assert "filtered" not in locations


def test_migrate_edges_edge_filter_with_node_filter(generic, creation_one):
    """Test edge_filter combined with node_filter"""
    # Create graph with multiple nodes
    graph = [
        {
            "name": "n1",
            "edges": [{"name": "e1"}],
        },
        {
            "name": "n2",
            "edges": [{"name": "e2"}],
        },
    ]
    # Node filter allows only n1, edge filter allows only edges with location "me!"
    migrate_edges(
        graph,
        creation_one,
        MigrationConfig(
            node_filter=lambda x: x.get("name") == "n1",
            edge_filter=lambda x: x.get("location") == "me!",
            verbs=["create"],
        ),
    )
    # n1 should have the new edge, n2 should not
    assert len(graph[0]["edges"]) == 2
    assert len(graph[1]["edges"]) == 1
    assert graph[0]["edges"][1]["name"] == "hey"


def test_migrate_edges_create_no_edge_filter(generic, creation_one):
    """Test create without edge_filter - edge should always be added"""
    assert len(generic[0]["edges"]) == 2
    migrate_edges(
        generic,
        creation_one,
        MigrationConfig(verbs=["create"]),
    )
    # Edge should be added when no edge_filter is provided
    assert len(generic[0]["edges"]) == 3
    assert generic[0]["edges"][2]["name"] == "hey"


def test_migrate_edges_edge_filter_all_edges_filtered(generic):
    """Test edge_filter when all edges are filtered out"""
    creation_data = {
        "create": [
            {
                "target": {
                    "name": "edge1",
                    "product": "p1",
                    "unit": "u1",
                    "location": "l1",
                },
            },
            {
                "target": {
                    "name": "edge2",
                    "product": "p2",
                    "unit": "u2",
                    "location": "l2",
                },
            },
        ]
    }
    assert len(generic[0]["edges"]) == 2
    # Filter that matches nothing
    migrate_edges(
        generic,
        creation_data,
        MigrationConfig(edge_filter=lambda x: False, verbs=["create"]),
    )
    # No edges should be added
    assert len(generic[0]["edges"]) == 2


def test_migrate_edges_edge_filter_all_edges_allowed(generic):
    """Test edge_filter when all edges pass the filter"""
    creation_data = {
        "create": [
            {
                "target": {
                    "name": "edge1",
                    "product": "p1",
                    "unit": "u1",
                    "location": "l1",
                },
            },
            {
                "target": {
                    "name": "edge2",
                    "product": "p2",
                    "unit": "u2",
                    "location": "l2",
                },
            },
        ]
    }
    assert len(generic[0]["edges"]) == 2
    # Filter that matches everything
    migrate_edges(
        generic,
        creation_data,
        MigrationConfig(edge_filter=lambda x: True, verbs=["create"]),
    )
    # All edges should be added
    assert len(generic[0]["edges"]) == 4


def test_migrate_edges_edge_filter_with_custom_edges_label(creation_one):
    """Test edge_filter with custom edges_label"""
    graph = [
        {
            "name": "n1",
            "flows": [{"name": "e1"}],  # Custom label "flows" instead of "edges"
        }
    ]
    # Filter allows only edges with location "me!"
    migrate_edges(
        graph,
        creation_one,
        MigrationConfig(
            edges_label="flows",
            edge_filter=lambda x: x.get("location") == "me!",
            verbs=["create"],
        ),
    )
    # Edge should be added because filter allows it
    assert len(graph[0]["flows"]) == 2
    assert graph[0]["flows"][1]["name"] == "hey"


def test_migrate_edges_edge_filter_with_custom_edges_label_filtered(creation_one):
    """Test edge_filter with custom edges_label when edge is filtered out"""
    graph = [
        {
            "name": "n1",
            "exchanges": [{"name": "e1"}],  # Custom label "exchanges"
        }
    ]
    # Filter prevents edges with location "me!"
    migrate_edges(
        graph,
        creation_one,
        MigrationConfig(
            edges_label="exchanges",
            edge_filter=lambda x: x.get("location") != "me!",
            verbs=["create"],
        ),
    )
    # Edge should NOT be added because filter prevents it
    assert len(graph[0]["exchanges"]) == 1
