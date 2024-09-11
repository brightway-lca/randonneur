from copy import deepcopy
from typing import List

from randonneur.config import MigrationConfig
from randonneur.utils import EXCLUDED_ATTRS, FlexibleLookupDict


def migrate_nodes_disaggregate(*args, **kwargs):
    raise NotImplemented


def migrate_nodes_replace(*args, **kwargs):
    raise NotImplemented


def migrate_nodes_update(
    graph: List[dict],
    migration_fld: FlexibleLookupDict,
    config: MigrationConfig,
) -> List[dict]:
    for node in graph:
        if config.node_filter and not config.node_filter(node):
            continue
        try:
            migration = migration_fld[node]
            node.update(migration["target"])
            if config.add_extra_attributes:
                node.update({k: v for k, v in migration.items() if k not in EXCLUDED_ATTRS})
        except KeyError:
            continue
    return node


def migrate_nodes_delete(
    graph: List[dict],
    migration_fld: FlexibleLookupDict,
    config: MigrationConfig,
) -> List[dict]:
    nodes_to_remove = set()

    for index, node in enumerate(graph):
        if config.node_filter and not config.node_filter(node):
            continue
        try:
            migration_fld[node]
            nodes_to_remove.add(index)
        except KeyError:
            continue
    if nodes_to_remove:
        # Sort from highest to allow modification in place
        for index in sorted(nodes_to_remove, reverse=True):
            del graph[index]
    return node


def migrate_nodes_create(
    graph: List[dict],
    migration_fld: List[dict],
    config: MigrationConfig,
) -> List[dict]:
    graph.extend([deepcopy(obj["target"]) for obj in migration_fld])
    return graph
