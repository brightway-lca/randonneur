from typing import Optional, Dict, Callable, List

from pydantic import BaseModel

from .utils import SAFE_VERBS


class MigrationConfig(BaseModel):
    """
    A class that stores configuration options for applying migrations.

    The following can be specified:

    `mapping`: Change the labels in the `migrations` data to match your data schema. `mapping`
    needs to be a dict with `source` and/or `target` keys, each value should be a dictionary with
    `{old_label: new_label}` pairs.

    ```python
    migrate_edges(
        graph=[{"edges": [{"name": "foo"}]}],
        migrations={"update": [{"source": {"not-name": "foo"}, "target": {"location": "bar"}}]},
        config=MigrationConfig(mapping={"source": {"not-name": "name"}})
    )
    >>> [{"edges": [{"name": "foo", "location": "bar"}]}]
    ```

    `node_filter`: A callable which determines if edges in that node should be modified. Returns
    `True` if the node *should be* modified.

    ```python
    migrate_edges(
        graph=[{"edges": [{"name": "foo"}]}],
        migrations={"update": [{"source": {"name": "foo"}, "target": {"location": "bar"}}]},
        config=MigrationConfig(node_filter=lambda node: node.get("sport") == "🏄‍♀️")
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
        migrations={"update": [
            {"source": {"name": "foo", "missing": "🔍"}, "target": {"location": "bar"}}
        ]},
        config=MigrationConfig(fields=["name"]),
    )
    >>> [{"edges": [{"name": "foo", "location": "bar"}]}]
    ```

    `verbose`: Display progress bars and more logging messages.

    `edges_label`: The label used for edges in the nodes of the `graph`. Defaults to `edges`.

    ```python
    migrate_edges(
        graph=[{"e": [{"name": "foo"}]}],
        migrations={"update": [{"source": {"name": "foo"}, "target": {"location": "bar"}}]},
        config=MigrationConfig(edges_label="e"),
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
    We need to write custom functions for each verb as they have difference behaviour.

    `case_sensitive`: Flag indicating whether to do case sensitive matching of transformations to
    nodes or edges in the graph. Default is false, as practical experience has shown us that cases
    get commonly changed by software developers or users. Only applies to string values.

    """

    mapping: Optional[Dict[str, dict]] = None
    node_filter: Optional[Callable] = None
    edge_filter: Optional[Callable] = None
    fields: Optional[List[str]] = None
    verbose: bool = False
    edges_label: str = "edges"
    verbs: List[str] = SAFE_VERBS
    case_sensitive: bool = False
    add_extra_attributes: bool = False
