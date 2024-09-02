from functools import partial
from pathlib import Path
from typing import List, Optional

from loguru import logger
from randonneur_data import Registry
from tqdm import tqdm

from .edge_functions import (
    migrate_edges_create,
    migrate_edges_delete,
    migrate_edges_disaggregate,
    migrate_edges_replace,
    migrate_edges_update,
)
from .errors import WrongGraphContext
from .utils import FlexibleLookupDict, apply_mapping
from .config import MigrationConfig

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
    """For each edge in each node in ``data``, check each transformation in ``migrations``. For each
    transformation for which there is a match, make the given changes to the edge.

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

    Returns `graph` with altered content.

    """
    config = config or MigrationConfig()
    progressbar = (
        partial(tqdm, desc="Transforming graph nodes") if config.verbose else lambda x: iter(x)
    )

    if config.mapping:
        migrations = apply_mapping(
            migrations=migrations, mapping=config.mapping, verbs=config.verbs
        )

    verbs = list(filter(lambda x: x in verb_dispatch and x in migrations, config.verbs))
    logger.info("Can apply the following transformation verbs: {v}", v=verbs)

    flds = {
        verb: FlexibleLookupDict(
            input_data=migrations[verb],
            fields_filter=config.fields,
            case_sensitive=config.case_sensitive,
        )
        for verb in verbs
    }

    if "create" in migrations and "create" in config.verbs:
        logger.warning(
            """`migrations` has `create` section - this will add exchanges to all nodes.
This is almost never the desired behaviour, consider removing `create` from the `verb` input."""
        )

    for node in progressbar(graph):
        if config.node_filter and not config.node_filter(node):
            continue

        for verb in verbs:
            verb_dispatch[verb](
                node=node,
                migration_fld=flds[verb],
                config=config,
            )

    return graph


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
