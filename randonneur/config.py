from typing import Callable, Dict, List, Optional

from pydantic import BaseModel

from randonneur.utils import SAFE_VERBS


class MigrationConfig(BaseModel):
    """
    A class that stores configuration options for applying migrations.

    The following can be specified:

    `mapping`: Change the labels in the `migrations` data to match your data schema. `mapping` can
    change the labels in the migration `source` and `target` sections. The `mapping` input should be
    a dict with keys "source" and "target", and have values of `{old_label: new_label}` pairs:

    ```python
    migrate_edges(
        graph=[{"edges": [{"name": "foo"}]}],
        migrations={"update": [{"source": {"not-name": "foo"}, "target": {"location": "bar"}}]},
        config=MigrationConfig(mapping={"source": {"not-name": "name"}})
    )
    >>> [{"edges": [{"name": "foo", "location": "bar"}]}]
    ```

    `node_filter`: A callable which determines whether or not the given node should be modified.
    Applies to both verbs and edges, with the exception of node creation - it doesn't make sense to
    filter existing nodes as we are creating new objects.

    `node_filter` needs to be a callable which takes a node object and returns a boolean which tells
    if the node *should* be modified. In this example, the filter returns `False` and the node isn't
    modified:

    ```python
    migrate_edges(
        graph=[{"edges": [{"name": "foo"}]}],
        migrations={"update": [{"source": {"name": "foo"}, "target": {"location": "bar"}}]},
        config=MigrationConfig(node_filter=lambda node: node.get("sport") == "🏄‍♀️")
    )
    >>> [{"edges": [{"name": "foo"}]}]
    ```

    `edge_filter`: A callable which determines whether or not the given edge should be modified.
    Applies only to edge transformations, and does *not* apply to edge creation, as this function is
    always called on the edge to modified, not on the transformation object.
    Returns

    `edge_filter` needs to be a callable which takes an edge object and returns a boolean which
    indicates if the edge *should* be modified.

    `fields`: A list of object keys as strings, used when checking if the given transformation
    matches the node or edge under consideration. In other words, only use the fields in `fields`
    when checking the `source` values in each transformation for a match. Each field in `fields`
    doesn't have to be in each transformation.

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

    `edges_label`: The label used for edges in the nodes of the `graph`. Defaults to "edges". In
    other data formats, this could be "flows" or "exchanges".

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

    The default value of `verbs` are the "safe" transformations - replace, update, and disaggregate.
    To get create and delete you need to specify them in the configuration.

    Only the verbs `create`, `disaggregate`, `replace`, `update`, and `delete` are used in our
    functions, regardless of what is given in `verbs`, as we don't know how to handle custom verbs.
    We need to write custom functions for each verb as they have difference behaviour.

    `case_sensitive`: Flag indicating whether to do case sensitive matching of transformations to
    nodes or edges in the graph. Default is false, as practical experience has shown us that cases
    get commonly changed by software developers or users. Only applies to string values.

    ```python
    migrate_edges(
        graph=[{"edges": [{"name": "foo"}]}],
        migrations={"update": [{"source": {"name": "FOO"}, "target": {"location": "bar"}}]},
        config=MigrationConfig(case_sensitive=False),
    )
    >>> [{"edges": [{"name": "foo", "location": "bar"}]}]
    ```

    `add_extra_attributes`: Flag indicating whether to include additional attributes when doing
    replace, update, and disaggregate changes. Extra attributes are defined outside the "source" and
    "target" transformation keys. Note that keys in `randonneur.utils.EXCLUDED_ATTRS` are never
    added.

    ```python
    migrate_edges(
        graph=[{"edges": [{"name": "foo"}]}],
        migrations={"update": [{
            "source": {"name": "FOO"},
            "target": {"location": "bar"},
            "comment": "Reason for change",
        }]},
        config=MigrationConfig(add_extra_attributes=True),
    )
    >>> [{"edges": [{"name": "foo", "location": "bar", "comment": "Reason for change"}]}]
    ```

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
