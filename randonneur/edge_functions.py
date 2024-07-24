from typing import Callable, Optional


def migrate_edges_create(
    node: dict,
    migrations: dict,
    fields: list,
    edges_label: str,
    verbose: bool,
    edge_filter: Optional[Callable] = None,
) -> dict:
    pass


def migrate_edges_delete(
    node: dict,
    migrations: dict,
    fields: list,
    edges_label: str,
    verbose: bool,
    edge_filter: Optional[Callable] = None,
) -> dict:
    pass


def migrate_edges_disaggregate(
    node: dict,
    migrations: dict,
    fields: list,
    edges_label: str,
    verbose: bool,
    edge_filter: Optional[Callable] = None,
) -> dict:
    pass


def migrate_edges_replace(
    node: dict,
    migrations: dict,
    fields: list,
    edges_label: str,
    verbose: bool,
    edge_filter: Optional[Callable] = None,
) -> dict:
    pass


def migrate_edges_update(
    node: dict,
    migrations: dict,
    fields: list,
    edges_label: str,
    verbose: bool,
    edge_filter: Optional[Callable] = None,
) -> dict:
    pass
