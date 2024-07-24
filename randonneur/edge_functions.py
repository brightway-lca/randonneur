from copy import deepcopy
from typing import Callable, List, Optional

from frozendict import frozendict

from .utils import matcher, rescale_edge


def migrate_edges_create(
    node: dict,
    migrations: List[dict],
    edges_label: str,
    verbose: bool,
    fields: Optional[List[str]] = None,
    edge_filter: Optional[Callable] = None,
) -> dict:
    pass


def migrate_edges_delete(
    node: dict,
    migrations: List[dict],
    edges_label: str,
    verbose: bool,
    fields: Optional[List[str]] = None,
    edge_filter: Optional[Callable] = None,
) -> dict:
    pass


def migrate_edges_disaggregate(
    node: dict,
    migrations: List[dict],
    edges_label: str,
    verbose: bool,
    fields: Optional[List[str]] = None,
    edge_filter: Optional[Callable] = None,
) -> dict:
    edges_to_add, edges_to_remove = [], set()

    for edge in node.get(edges_label, []):
        if edge_filter and not edge_filter(edge):
            continue
        for migration in migrations:
            if matcher(source=migration["source"], target=edge, fields=fields):
                for allocated in migration["targets"]:
                    new_edge = rescale_edge(deepcopy(edge), allocated["allocation"])
                    new_edge.update(allocated)
                    edges_to_add.append(new_edge)
                edges_to_remove.add(frozendict(edge))
    if edges_to_remove:
        node[edges_label] = [
            edge
            for edge in node[edges_label]
            if frozendict(edge) not in edges_to_remove
        ] + edges_to_add

    return node


def migrate_edges_replace(
    node: dict,
    migrations: List[dict],
    edges_label: str,
    verbose: bool,
    fields: Optional[List[str]] = None,
    edge_filter: Optional[Callable] = None,
) -> dict:
    for edge in node.get(edges_label, []):
        if edge_filter and not edge_filter(edge):
            continue
        for migration in migrations:
            if matcher(source=migration["source"], target=edge, fields=fields):
                if "allocation" in migration["target"]:
                    rescale_edge(edge, migration["target"]["allocation"])
                edge.update(migration["target"])

    return node


def migrate_edges_update(
    node: dict,
    migrations: List[dict],
    edges_label: str,
    verbose: bool,
    fields: Optional[List[str]] = None,
    edge_filter: Optional[Callable] = None,
) -> dict:
    """Difference is in intent of data developer, not in implementation."""
    return migrate_edges_replace(
        node=node,
        migrations=migrations,
        fields=fields,
        edges_label=edges_label,
        verbose=verbose,
        edge_filter=edge_filter,
    )
