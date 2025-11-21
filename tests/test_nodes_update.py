import pytest

from randonneur import MigrationConfig
from randonneur.node_functions import migrate_nodes_update
from randonneur.utils import FlexibleLookupDict


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
            "name": "n2",
            "reference product": "rp2",
            "location": "l2",
            "unit": "u2",
            "foo": "baz",
        },
    ]


@pytest.fixture
def update_migration():
    return [
        {
            "source": {
                "name": "n1",
                "location": "l1",
            },
            "target": {
                "location": "l1_updated",
                "new_field": "new_value",
            },
        }
    ]


@pytest.fixture
def update_migration_multiple():
    return [
        {
            "source": {
                "name": "n1",
                "location": "l1",
            },
            "target": {
                "location": "l1_updated",
            },
        },
        {
            "source": {
                "name": "n2",
                "location": "l2",
            },
            "target": {
                "location": "l2_updated",
            },
        },
    ]


def test_migrate_nodes_update_simple(generic, update_migration):
    """Test basic node update functionality"""
    migration_fld = FlexibleLookupDict(update_migration)
    result = migrate_nodes_update(generic, migration_fld, MigrationConfig())
    
    # Function should return the graph
    assert result is generic
    
    # n1 should be updated
    assert generic[0]["location"] == "l1_updated"
    assert generic[0]["new_field"] == "new_value"
    assert generic[0]["name"] == "n1"  # Original fields preserved
    assert generic[0]["foo"] == "bar"
    
    # n2 should remain unchanged
    assert generic[1]["location"] == "l2"
    assert "new_field" not in generic[1]


def test_migrate_nodes_update_node_filter_prevents_update(generic, update_migration):
    """Test node_filter preventing node update when filter returns False"""
    migration_fld = FlexibleLookupDict(update_migration)
    result = migrate_nodes_update(
        generic,
        migration_fld,
        MigrationConfig(node_filter=lambda x: x.get("name") != "n1"),
    )
    
    # n1 should NOT be updated because filter returns False
    assert generic[0]["location"] == "l1"
    assert "new_field" not in generic[0]
    
    # n2 should remain unchanged (no matching migration anyway)
    assert generic[1]["location"] == "l2"


def test_migrate_nodes_update_node_filter_allows_update(generic, update_migration):
    """Test node_filter allowing node update when filter returns True"""
    migration_fld = FlexibleLookupDict(update_migration)
    result = migrate_nodes_update(
        generic,
        migration_fld,
        MigrationConfig(node_filter=lambda x: x.get("name") == "n1"),
    )
    
    # n1 should be updated because filter returns True
    assert generic[0]["location"] == "l1_updated"
    assert generic[0]["new_field"] == "new_value"
    
    # n2 should remain unchanged
    assert generic[1]["location"] == "l2"


def test_migrate_nodes_update_multiple_nodes(generic, update_migration_multiple):
    """Test updating multiple nodes"""
    migration_fld = FlexibleLookupDict(update_migration_multiple)
    result = migrate_nodes_update(generic, migration_fld, MigrationConfig())
    
    # Both nodes should be updated
    assert generic[0]["location"] == "l1_updated"
    assert generic[1]["location"] == "l2_updated"
    
    # Original fields preserved
    assert generic[0]["name"] == "n1"
    assert generic[1]["name"] == "n2"


def test_migrate_nodes_update_no_matching_migration(generic):
    """Test when no migration matches any node"""
    update_migration = [
        {
            "source": {
                "name": "nonexistent",
                "location": "nowhere",
            },
            "target": {
                "location": "updated",
            },
        }
    ]
    migration_fld = FlexibleLookupDict(update_migration)
    original_n1 = generic[0].copy()
    original_n2 = generic[1].copy()
    
    result = migrate_nodes_update(generic, migration_fld, MigrationConfig())
    
    # Function should return the graph even when no updates occur
    assert result is generic
    
    # No nodes should be changed
    assert generic[0] == original_n1
    assert generic[1] == original_n2


def test_migrate_nodes_update_add_extra_attributes(generic, update_migration):
    """Test add_extra_attributes flag adding extra fields from migration"""
    # Add extra attributes to migration
    update_migration[0]["comment"] = "This is a comment"
    update_migration[0]["reason"] = "Update reason"
    
    migration_fld = FlexibleLookupDict(update_migration)
    result = migrate_nodes_update(
        generic,
        migration_fld,
        MigrationConfig(add_extra_attributes=True),
    )
    
    # n1 should have extra attributes added
    assert generic[0]["location"] == "l1_updated"
    assert generic[0]["new_field"] == "new_value"
    assert generic[0]["comment"] == "This is a comment"
    assert generic[0]["reason"] == "Update reason"
    
    # n2 should remain unchanged
    assert "comment" not in generic[1]
    assert "reason" not in generic[1]


def test_migrate_nodes_update_add_extra_attributes_false(generic, update_migration):
    """Test that extra attributes are NOT added when add_extra_attributes is False"""
    update_migration[0]["comment"] = "This is a comment"
    
    migration_fld = FlexibleLookupDict(update_migration)
    result = migrate_nodes_update(
        generic,
        migration_fld,
        MigrationConfig(add_extra_attributes=False),
    )
    
    # n1 should be updated but without extra attributes
    assert generic[0]["location"] == "l1_updated"
    assert "comment" not in generic[0]


def test_migrate_nodes_update_excluded_attrs_not_added(generic, update_migration):
    """Test that excluded attributes are never added even with add_extra_attributes=True"""
    # Add extra attributes to migration (but not excluded ones as top-level keys)
    # Note: target, targets, source are required by FlexibleLookupDict structure
    # We test that these keys from EXCLUDED_ATTRS are not added to the node
    update_migration[0]["conversion_factor"] = 2.0
    update_migration[0]["comment"] = "This should be added"
    update_migration[0]["reason"] = "Update reason"
    
    migration_fld = FlexibleLookupDict(update_migration)
    result = migrate_nodes_update(
        generic,
        migration_fld,
        MigrationConfig(add_extra_attributes=True, add_conversion_factor_to_nodes=False),
    )
    
    # conversion_factor should NOT be added as an extra attribute (it's in EXCLUDED_ATTRS)
    # but comment and reason should be added
    assert generic[0]["comment"] == "This should be added"
    assert generic[0]["reason"] == "Update reason"
    # conversion_factor should not be added via add_extra_attributes
    # (it would only be added via add_conversion_factor_to_nodes, which is False)
    assert "conversion_factor" not in generic[0]


def test_migrate_nodes_update_conversion_factor_new(generic, update_migration):
    """Test add_conversion_factor_to_nodes when node has no existing conversion_factor"""
    update_migration[0]["conversion_factor"] = 2.5
    
    migration_fld = FlexibleLookupDict(update_migration)
    result = migrate_nodes_update(
        generic,
        migration_fld,
        MigrationConfig(add_conversion_factor_to_nodes=True),
    )
    
    # n1 should have conversion_factor set
    assert generic[0]["conversion_factor"] == 2.5
    
    # n2 should not have conversion_factor
    assert "conversion_factor" not in generic[1]


def test_migrate_nodes_update_conversion_factor_existing(generic, update_migration):
    """Test add_conversion_factor_to_nodes multiplying existing conversion_factor"""
    generic[0]["conversion_factor"] = 2.0
    update_migration[0]["conversion_factor"] = 3.0
    
    migration_fld = FlexibleLookupDict(update_migration)
    result = migrate_nodes_update(
        generic,
        migration_fld,
        MigrationConfig(add_conversion_factor_to_nodes=True),
    )
    
    # n1 should have multiplied conversion_factor
    assert generic[0]["conversion_factor"] == 6.0  # 2.0 * 3.0


def test_migrate_nodes_update_conversion_factor_default_one(generic, update_migration):
    """Test add_conversion_factor_to_nodes using default 1.0 when node has no conversion_factor"""
    update_migration[0]["conversion_factor"] = 2.5
    
    migration_fld = FlexibleLookupDict(update_migration)
    result = migrate_nodes_update(
        generic,
        migration_fld,
        MigrationConfig(add_conversion_factor_to_nodes=True),
    )
    
    # n1 should have conversion_factor = 1.0 * 2.5 = 2.5
    assert generic[0]["conversion_factor"] == 2.5


def test_migrate_nodes_update_conversion_factor_false(generic, update_migration):
    """Test that conversion_factor is NOT added when add_conversion_factor_to_nodes is False"""
    update_migration[0]["conversion_factor"] = 2.5
    
    migration_fld = FlexibleLookupDict(update_migration)
    result = migrate_nodes_update(
        generic,
        migration_fld,
        MigrationConfig(add_conversion_factor_to_nodes=False),
    )
    
    # n1 should be updated but without conversion_factor
    assert generic[0]["location"] == "l1_updated"
    assert "conversion_factor" not in generic[0]


def test_migrate_nodes_update_conversion_factor_no_factor_in_migration(generic, update_migration):
    """Test that conversion_factor is not modified when migration has no conversion_factor"""
    generic[0]["conversion_factor"] = 2.0
    
    migration_fld = FlexibleLookupDict(update_migration)
    result = migrate_nodes_update(
        generic,
        migration_fld,
        MigrationConfig(add_conversion_factor_to_nodes=True),
    )
    
    # n1 should keep original conversion_factor
    assert generic[0]["conversion_factor"] == 2.0


def test_migrate_nodes_update_combines_all_features(generic, update_migration):
    """Test combining node_filter, add_extra_attributes, and add_conversion_factor_to_nodes"""
    update_migration[0]["comment"] = "Updated node"
    update_migration[0]["conversion_factor"] = 1.5
    generic[0]["conversion_factor"] = 2.0
    
    migration_fld = FlexibleLookupDict(update_migration)
    result = migrate_nodes_update(
        generic,
        migration_fld,
        MigrationConfig(
            node_filter=lambda x: x.get("name") == "n1",
            add_extra_attributes=True,
            add_conversion_factor_to_nodes=True,
        ),
    )
    
    # n1 should have all updates
    assert generic[0]["location"] == "l1_updated"
    assert generic[0]["new_field"] == "new_value"
    assert generic[0]["comment"] == "Updated node"
    assert generic[0]["conversion_factor"] == 3.0  # 2.0 * 1.5
    
    # n2 should remain unchanged
    assert generic[1]["location"] == "l2"
    assert "comment" not in generic[1]
    assert "conversion_factor" not in generic[1]


def test_migrate_nodes_update_partial_match(generic):
    """Test update with partial field matching"""
    update_migration = [
        {
            "source": {
                "name": "n1",
            },
            "target": {
                "location": "l1_partial",
            },
        }
    ]
    
    migration_fld = FlexibleLookupDict(update_migration)
    result = migrate_nodes_update(generic, migration_fld, MigrationConfig())
    
    # n1 should be updated based on name match
    assert generic[0]["location"] == "l1_partial"
    assert generic[0]["name"] == "n1"


def test_migrate_nodes_update_overwrites_existing_fields(generic, update_migration):
    """Test that target fields overwrite existing node fields"""
    generic[0]["new_field"] = "old_value"
    
    migration_fld = FlexibleLookupDict(update_migration)
    result = migrate_nodes_update(generic, migration_fld, MigrationConfig())
    
    # new_field should be overwritten
    assert generic[0]["new_field"] == "new_value"
    assert generic[0]["location"] == "l1_updated"


def test_migrate_nodes_update_empty_graph(update_migration):
    """Test update with empty graph"""
    graph = []
    migration_fld = FlexibleLookupDict(update_migration)
    result = migrate_nodes_update(graph, migration_fld, MigrationConfig())
    
    # Graph should remain empty and function should return the graph
    assert graph == []
    assert result == graph
    assert result is graph  # Should return the same list object


def test_migrate_nodes_update_empty_migration(generic):
    """Test update with empty migration list"""
    migration_fld = FlexibleLookupDict([])
    original_n1 = generic[0].copy()
    original_n2 = generic[1].copy()
    
    result = migrate_nodes_update(generic, migration_fld, MigrationConfig())
    
    # No nodes should be changed
    assert generic[0] == original_n1
    assert generic[1] == original_n2

