from functools import partial
from pathlib import Path
from typing import Callable, List, Optional

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
from .utils import SAFE_VERBS, FlexibleLookupDict, apply_mapping

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
    mapping: Optional[dict] = None,
    node_filter: Optional[Callable] = None,
    edge_filter: Optional[Callable] = None,
    fields: Optional[list] = None,
    verbose: bool = False,
    edges_label: str = "edges",
    verbs: List[str] = SAFE_VERBS,
    case_sensitive: bool = False,
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

    The changes can be customized with the additional input arguments:

    `mapping`: Change the labels in `migrations` to match your data schema. `mapping` needs to be a
    dict with `source` and/or `target` keys, each value should be a dictionary with
    `{old_label: new_label}` pairs.

    ```python
    migrate_edges(
        graph=[{"edges": [{"name": "foo"}]}],
        migrations={"update": [{"source": {"not-name": "foo"}, "target": {"location": "bar"}}]},
        mapping={"source": {"not-name": "name"}}
    )
    >>> [{"edges": [{"name": "foo", "location": "bar"}]}]
    ```

    `node_filter`: A callable which determines if edges in that node should be modified. Returns
    `True` if the node *should be* modified.

    ```python
    migrate_edges(
        graph=[{"edges": [{"name": "foo"}]}],
        migrations={"update": [{"source": {"name": "foo"}, "target": {"location": "bar"}}]},
        node_filter=lambda node: node.get("sport") == "🏄‍♀️"
    )
    >>> [{"edges": [{"name": "foo"}]}]
    ```

    `edge_filter`: A callable which determines if a specific edge should be modified. Returns
    `True` if the edge *should be* modified.

    `fields`: A list of strings used when checking if the given transformation matches the edge
    under consideration. In other words, only use the fields in `fields` when checking the `source`
    values in each transformation for a match. Each field in `fields` doesn't have to be in each
    transformation.

    ```python
    migrate_edges(
        graph=[{"edges": [{"name": "foo"}]}],
        migrations={"update": [{"source": {"name": "foo", "missing": "🔍"}, "target": {"location": "bar"}}]},
        fields=["name"],
    )
    >>> [{"edges": [{"name": "foo", "location": "bar"}]}]
    ```

    `verbose`: Display progress bars and more logging messages.

    `edges_label`: The label used for edges in the nodes of the `graph`. Defaults to `edges`.

    ```python
    migrate_edges(
        graph=[{"e": [{"name": "foo"}]}],
        migrations={"update": [{"source": {"name": "foo"}, "target": {"location": "bar"}}]},
        edges_label="e",
    )
    >>> [{"edges": [{"name": "foo", "location": "bar"}]}]
    ```

    `verbs`: The list of transformation types from `migrations` to apply. Transformations are run
    in the order as given in `verbs`, and in some complicated cases you may want to keep the same
    verbs but change their order to get the desired output state. In general, such complicated
    transformations should be broken down to smaller discrete and independent transformations
    whenever possible, and logs checked carefully after their application.

    Only the verbs `create`, `disaggregate`, `replace`, `update`, and `delete` are used in this
    function, regardless of what is given in `verbs`, as we don't know how to handle custom verbs.

    `case_sensitive`: Flag indicating whether to do case sensitive matching of transformations to
    nodes or edges in the graph. Default is false, as practical experience has shown us that cases
    get commonly changed by software developers or users.

    Returns `graph` with altered content.

    """
    progressbar = partial(tqdm, desc="Transforming graph nodes") if verbose else lambda x: iter(x)

    if mapping:
        migrations = apply_mapping(migrations=migrations, mapping=mapping, verbs=verbs)

    verbs = list(filter(lambda x: x in verb_dispatch and x in migrations, verbs))
    logger.info("Can apply the following transformation verbs: {v}", v=verbs)

    flds = {
        verb: FlexibleLookupDict(
            input_data=migrations[verb], fields_filter=fields, case_sensitive=case_sensitive
        )
        for verb in verbs
    }

    if "create" in migrations and "create" in verbs:
        logger.warning(
            """`migrations` has `create` section - this will add exchanges to all nodes.
This is almost never the desired behaviour, consider removing `create` from the `verb` input."""
        )

    for node in progressbar(graph):
        if node_filter and not node_filter(node):
            continue

        for verb in verbs:
            verb_dispatch[verb](
                node=node,
                migration_fld=flds[verb],
                edge_filter=edge_filter,
                edges_label=edges_label,
                verbose=verbose,
            )

    return graph


def migrate_edges_with_stored_data(
    graph: List[dict],
    label: str,
    data_registry_path: Optional[Path] = None,
    mapping: Optional[dict] = None,
    node_filter: Optional[Callable] = None,
    edge_filter: Optional[Callable] = None,
    fields: Optional[list] = None,
    verbose: bool = False,
    edges_label: str = "edges",
    verbs: List[str] = SAFE_VERBS,
    case_sensitive: bool = False,
) -> List[dict]:
    """A simple wrapper to load from a `randonneur_data.Registry` with some basic sanity checks."""
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
        mapping=mapping,
        node_filter=node_filter,
        edge_filter=edge_filter,
        fields=fields,
        verbose=verbose,
        edges_label=edges_label,
        verbs=verbs,
        case_sensitive=case_sensitive,
    )
