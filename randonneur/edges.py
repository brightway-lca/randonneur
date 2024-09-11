from pathlib import Path
from typing import List, Optional

from loguru import logger
from randonneur_data import Registry

from randonneur.config import MigrationConfig
from randonneur.edge_functions import (
    migrate_edges_create,
    migrate_edges_delete,
    migrate_edges_disaggregate,
    migrate_edges_replace,
    migrate_edges_update,
)
from randonneur.errors import WrongGraphContext
from randonneur.generic_transformation import generic_transformation

verb_dispatch = {
    "create": migrate_edges_create,
    "replace": migrate_edges_replace,
    "delete": migrate_edges_delete,
    "update": migrate_edges_update,
    "disaggregate": migrate_edges_disaggregate,
}


def migrate_edges(
    graph: List[dict],
    migrations: dict,
    config: Optional[MigrationConfig] = None,
) -> List[dict]:
    """For each edge in each node in ``graph``, check each transformation in ``migrations``. For
    each transformation for which there is a match, make the given changes to the edge.

    Here is an example:

    ```python
    migrate_edges(
        graph=[{"edges": [{"name": "foo"}]}],
        migrations={"update": [{"source": {"name": "foo"}, "target": {"location": "bar"}}]},
    )
    >>> [{"edges": [{"name": "foo", "location": "bar"}]}]
    ```

    The changes can be customized with a `MigrationConfig` object. See the `MigrationConfig` docs
    for information on its input arguments.

    *Changes graph in place*, and returns `graph` with altered content.

    """
    return generic_transformation(
        graph=graph,
        migrations=migrations,
        verb_dispatch=verb_dispatch,
        is_edges=True,
        config=config,
    )


def migrate_edges_with_stored_data(
    graph: List[dict],
    label: str,
    data_registry_path: Optional[Path] = None,
    config: Optional[MigrationConfig] = None,
) -> List[dict]:
    """A simple wrapper to load from a `randonneur_data.Registry` with some basic sanity checks."""
    config = config or MigrationConfig()

    try:
        migrations = Registry(data_registry_path).get_file(label)
        logger.info(
            "Loaded transformation data {l} from registry with following verbs: {v}",
            l=label,
            v=[k for k in migrations if k in verb_dispatch],
        )
    except KeyError:
        raise KeyError(f"Transformation {label} not found in given transformation registry")

    if "edges" not in migrations.get("graph_context", []):
        raise WrongGraphContext(f"{label} migration can't be used on edges")

    return migrate_edges(
        graph=graph,
        migrations=migrations,
        config=config,
    )
