from copy import deepcopy
from typing import Callable, List, Optional

from .utils import rescale_edge

EXCLUDED_ATTRS = ("target", "targets", "source", "conversion_factor")


def migrate_edges_create(
    node: dict,
    migration_fld: dict,
    config: dict,
) -> dict:
    pass


def migrate_edges_delete(
    node: dict,
    migration_fld: dict,
    config: dict,
) -> dict:
    pass


def migrate_edges_disaggregate(
    node: dict,
    migration_fld: dict,
    config: dict,
) -> dict:
    edges_to_add, edges_to_remove = [], set()

    for edge in node.get(config.edges_label, []):
        if config.edge_filter and not config.edge_filter(edge):
            continue
        try:
            for allocated in migration_fld[edge]["targets"]:
                new_edge = rescale_edge(deepcopy(edge), allocated["allocation"])
                new_edge.update(allocated)
                if config.add_extra_attributes:
                    new_edge.update(
                        {k: v for k, v in migration_fld[edge].items() if k not in EXCLUDED_ATTRS}
                    )
                edges_to_add.append(new_edge)
            edges_to_remove.add(id(edge))
        except KeyError:
            continue
    if edges_to_remove:
        node[config.edges_label] = [
            edge for edge in node[config.edges_label] if id(edge) not in edges_to_remove
        ] + edges_to_add

    return node


def migrate_edges_replace(
    node: dict,
    migration_fld: dict,
    config: dict,
) -> dict:
    for edge in node.get(config.edges_label, []):
        if config.edge_filter and not config.edge_filter(edge):
            continue
        try:
            migration = migration_fld[edge]
            if "conversion_factor" in migration["target"]:
                rescale_edge(edge, migration["target"]["conversion_factor"])
            elif "allocation" in migration["target"]:
                rescale_edge(edge, migration["target"]["allocation"])
            edge.update(migration["target"])
            if config.add_extra_attributes:
                edge.update({k: v for k, v in migration.items() if k not in EXCLUDED_ATTRS})
        except KeyError:
            continue
    return node


def migrate_edges_update(
    node: dict,
    migration_fld: dict,
    config: dict,
) -> dict:
    """Difference is in intent of data developer, not in implementation."""
    return migrate_edges_replace(
        node=node,
        migration_fld=migration_fld,
        config=config,
    )
