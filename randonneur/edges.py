from copy import deepcopy
from pathlib import Path
from typing import Callable, List, Optional

from frozendict import frozendict
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
from .utils import SAFE_VERBS, apply_mapping, matcher


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

    Returns `graph` with altered content.

    """
    progressbar = tqdm if verbose else lambda x: iter(x)

    if mapping:
        migrations = apply_mapping(migrations=migrations, mapping=mapping, verbs=verbs)

    for node in progressbar(graph):
        if node_filter and not node_filter(node):
            continue

        if "create" in migrations and "create" in verbs:
            logger.warning(
                """`migrations` has `create` section - this will add exchanges to all nodes.
This is almost never the desired behaviour, consider removing `create` from the `verb` input."""
            )

        for verb in filter(lambda x: x in verb_dispatch, verbs):
            verb_dispatch[verb](
                node=node,
                migrations=migrations,
                edge_filter=edge_filter,
                fields=fields,
                edges_label=edges_label,
                verbose=verbose,
            )

    return graph

    #     exchanges_to_delete = set()
    #     exchanges_to_add = [
    #         obj["source"]
    #         for obj in migration_data.get("create-exchanges", [])
    #         if matcher(obj["dataset"], dataset)
    #     ]
    #     exchanges = dataset.get("exchanges", [])

    #     for exchange in exchanges:
    #         found = False

    #         if exchange_filter is not None and not exchange_filter(exchange):
    #             continue

    #         for possible in migration_data.get("delete", []):
    #             if (
    #                 not (found and only_one_change)
    #                 and matcher(possible, exchange)
    #                 and maybe_filter(possible.get("dataset"), dataset)
    #             ):
    #                 exchanges_to_delete.add(frozendict(exchange))
    #                 found = True

    #         for possible in migration_data.get("replace", []):
    #             if (
    #                 not (found and only_one_change)
    #                 and matcher(possible["source"], exchange)
    #                 and maybe_filter(possible.get("dataset"), dataset)
    #             ):
    #                 new_exchange = deepcopy(possible["target"])
    #                 # TBD: rescale uncertainty
    #                 new_exchange["amount"] = exchange["amount"] * new_exchange.pop(
    #                     "allocation", 1.0
    #                 )
    #                 exchanges_to_add.append(new_exchange)
    #                 exchanges_to_delete.add(frozendict(exchange))
    #                 found = True

    #         for possible in migration_data.get("update", []):
    #             if (
    #                 not (found and only_one_change)
    #                 and matcher(possible["source"], exchange)
    #                 and maybe_filter(possible.get("dataset"), dataset)
    #             ):
    #                 new_values = deepcopy(possible["target"])
    #                 exchange["amount"] *= new_values.pop("allocation", 1.0)
    #                 exchange.update(new_values)
    #                 found = True

    #         for possibles in migration_data.get("disaggregate", []):
    #             if (
    #                 not (found and only_one_change)
    #                 and matcher(possibles["source"], exchange)
    #                 and maybe_filter(possibles.get("dataset"), dataset)
    #             ):
    #                 for possible in possibles["targets"]:
    #                     base_exchange, new_exchange = deepcopy(exchange), deepcopy(
    #                         possible
    #                     )
    #                     base_exchange["amount"] = base_exchange[
    #                         "amount"
    #                     ] * new_exchange.pop("allocation", 1.0)
    #                     base_exchange.update(new_exchange)
    #                     exchanges_to_add.append(base_exchange)
    #                 exchanges_to_delete.add(frozendict(exchange))
    #                 found = True

    #     if exchanges_to_delete:
    #         exchanges = [
    #             exchange
    #             for exchange in exchanges
    #             if frozendict(exchange) not in exchanges_to_delete
    #         ]
    #     if exchanges_to_add:
    #         exchanges.extend(exchanges_to_add)
    #     dataset["exchanges"] = exchanges
    # return graph


def stored_migration_edges(
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
) -> List[dict]:
    """A simple wrapper to load from `randonneur_data.Registry` with some basic sanity checks."""
    try:
        migrations = Registry(data_registry_path)[label]
        logger.info(f"Loaded transformation data {label} from registry")
    except KeyError:
        raise KeyError(
            f"Transformation {label} not found in given transformation registry"
        )

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
    )
