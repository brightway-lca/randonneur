from copy import deepcopy
from typing import Callable, List, Optional

from frozendict import frozendict

from .utils import rescale_edge


def migrate_edges_create(
    node: dict,
    migration_fld: dict,
    edges_label: str,
    verbose: bool,
    edge_filter: Optional[Callable] = None,
) -> dict:
    pass


def migrate_edges_delete(
    node: dict,
    migration_fld: dict,
    edges_label: str,
    verbose: bool,
    edge_filter: Optional[Callable] = None,
) -> dict:
    pass


def migrate_edges_disaggregate(
    node: dict,
    migration_fld: dict,
    edges_label: str,
    verbose: bool,
    fields: Optional[List[str]] = None,
    edge_filter: Optional[Callable] = None,
    case_sensitive: bool = False,
) -> dict:
    edges_to_add, edges_to_remove = [], set()

    for edge in node.get(edges_label, []):
        if edge_filter and not edge_filter(edge):
            continue
        try:
            for allocated in migration_fld[edge]["targets"]:
                new_edge = rescale_edge(deepcopy(edge), allocated["allocation"])
                new_edge.update(allocated)
                edges_to_add.append(new_edge)
            edges_to_remove.add(id(edge))
        except KeyError:
            continue
    if edges_to_remove:
        node[edges_label] = [
            edge for edge in node[edges_label] if id(edge) not in edges_to_remove
        ] + edges_to_add

    return node


def migrate_edges_replace(
    node: dict,
    migration_fld: dict,
    edges_label: str,
    verbose: bool,
    fields: Optional[List[str]] = None,
    edge_filter: Optional[Callable] = None,
    case_sensitive: bool = False,
) -> dict:
    for edge in node.get(edges_label, []):
        if edge_filter and not edge_filter(edge):
            continue
        try:
            migration = migration_fld[edge]
            if "allocation" in migration["target"]:
                rescale_edge(edge, migration["target"]["allocation"])
            edge.update(migration["target"])
        except KeyError:
            continue
    return node


def migrate_edges_update(
    node: dict,
    migration_fld: dict,
    edges_label: str,
    verbose: bool,
    fields: Optional[List[str]] = None,
    edge_filter: Optional[Callable] = None,
    case_sensitive: bool = False,
) -> dict:
    """Difference is in intent of data developer, not in implementation."""
    return migrate_edges_replace(
        node=node,
        migration_fld=migration_fld,
        fields=fields,
        edges_label=edges_label,
        verbose=verbose,
        edge_filter=edge_filter,
        case_sensitive=case_sensitive,
    )
