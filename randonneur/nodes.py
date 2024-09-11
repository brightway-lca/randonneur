from pathlib import Path
from typing import List, Optional

from loguru import logger
from randonneur_data import Registry

from randonneur.config import MigrationConfig
from randonneur.errors import WrongGraphContext
from randonneur.generic_transformation import generic_transformation
from randonneur.node_functions import (
    migrate_nodes_create,
    migrate_nodes_delete,
    migrate_nodes_disaggregate,
    migrate_nodes_replace,
    migrate_nodes_update,
)

verb_dispatch = {
    "create": migrate_nodes_create,
    "replace": migrate_nodes_replace,
    "delete": migrate_nodes_delete,
    "update": migrate_nodes_update,
    "disaggregate": migrate_nodes_disaggregate,
}


def migrate_nodes(
    graph: List[dict],
    migrations: dict,
    config: Optional[MigrationConfig] = None,
) -> List[dict]:
    """For each node in ``graph``, check each transformation in ``migrations``. For each
    transformation for which there is a match, make the given changes to the node.

    Here is an example:

    ```python
    migrate_nodes(
        graph=[{"name": "foo"}],
        migrations={"update": [{"source": {"name": "foo"}, "target": {"location": "bar"}}]},
    )
    >>> [{"name": "foo", "location": "bar"}]
    ```

    The changes can be customized with a `MigrationConfig` object. See the `MigrationConfig` docs
    for information on its input arguments.

    *Changes graph in place*, and returns `graph` with altered content.

    """
    return generic_transformation(
        graph=graph,
        migrations=migrations,
        verb_dispatch=verb_dispatch,
        is_edges=False,
        config=config,
    )


def migrate_nodes_with_stored_data(
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

    if "nodes" not in migrations.get("graph_context", []):
        raise WrongGraphContext(f"{label} migration can't be used on nodes")

    return migrate_nodes(
        graph=graph,
        migrations=migrations,
        config=config,
    )
