<img src="logo/randonneur_logo_horizontal/randonneur.png">

Randonneur is a library to make changes to life cycle inventory databases. Specifically, `randonneur` provides the following:

* A data format for specifying life cycle inventory data transformations
* Helper functions to create and validate data in this data format
* Functions to apply the transformations to data

You can use it to re-link your data to the latest version of a background database, to update existing databases with new data, or to perform other data transformations. Randonneur uses JSON files to describe these changes; contrast this with [wurst](https://github.com/polca/wurst), which can do these manipulations and more, but documents its manipulations in code.

Another important difference with `wurst` is that `randoneur` does not have a fixed data schema - the schema is defined in each file.

`randonneur` does not provide any data itself, but its sister library [randonneur_data](https://github.com/brightway-lca/randonneur_data) has data for many common transformations.

Although designed to work with [Brightway](https://brightway.dev/), this library is not Brightway-specific.

[![PyPI](https://img.shields.io/pypi/v/randonneur.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/randonneur.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/randonneur)][pypi status]
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)][license]

[![Python 🐍 CI/CD tests](https://github.com/brightway-lca/randonneur/actions/workflows/python-test.yml/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/brightway-lca/randonneur/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]

[pypi status]: https://pypi.org/project/randonneur/
[tests]: https://github.com/brightway-lca/randonneur/actions/workflows/python-test.yml
[codecov]: https://app.codecov.io/gh/brightway-lca/randonneur
[pre-commit]: https://github.com/pre-commit/pre-commit

## Usage

### Generic usage pattern

* Extract a `randonneur` data migration file, normally from [randonneur_data](https://github.com/brightway-lca/randonneur_data) using `randonneur_data.Registry().get_file()`
* Extract an inventory database; this can be in the [common Brightway inventory format](https://github.com/brightway-lca/bw_interface_schemas), but you can also roll your own.
* Apply the data transformation using `migrate_edges`, optionally specifying the fields used for matching the transformation data, any mappings necessary to make the transformation data schema fit into your data schema, what filters should be applied to the input data (if any), and which verbs (`create`, `replace`, `update`, `delete`, or `disaggregate`) you want to apply.
* Load the modified data back into a suitable data store.

Here's a basic example:

```python
In [1]: import randonneur as rn
   ...: import randonneur_data as rd
   ...:

In [2]: my_lci = [{
   ...:     'name': "my process",
   ...:     'edges': [{
   ...:         'name': 'Xylene {RER}| xylene production | Cut-off, U',
   ...:         'amount': 1.0
   ...:     }]
   ...: }]
   ...:

In [3]: transformed = rn.migrate_edges_with_stored_data(
   ...:     my_lci,
   ...:     'simapro-ecoinvent-3.9.1-cutoff',
   ...:     config=rn.MigrationConfig(fields=['name'])
   ...: )
   ...: transformed
   ...:
Out[3]:
[{'name': 'my process',
  'edges': [{
    'name': 'xylene production',
    'amount': 1.0,
    'filename': '38175dbb-3f48-592c-83f1-c1f667c4b8fd_43c61790-cbeb-493e-8836-279a12ce3e43.spold',
    'location': 'RER',
    'reference product': 'xylene',
    'unit': 'kg'}]}]

In [4]: rn.migrate_edges_with_stored_data(
   ...:     transformed,
   ...:     'ecoinvent-3.9.1-cutoff-ecoinvent-3.10-cutoff',
   ...: )
   ...:
Out[4]:
[{'name': 'my process',
  'edges': [{'name': 'BTX production, from pyrolysis gas, average',
    'amount': 0.11757529360371775,
    'filename': '38175dbb-3f48-592c-83f1-c1f667c4b8fd_43c61790-cbeb-493e-8836-279a12ce3e43.spold',
    'location': 'RER',
    'reference product': 'xylene, mixed',
    'unit': 'kg',
    'allocation': 0.11757529360371775},
   {'name': 'BTX production, from reformate, average',
    'amount': 0.8824247063962822,
    'filename': '38175dbb-3f48-592c-83f1-c1f667c4b8fd_43c61790-cbeb-493e-8836-279a12ce3e43.spold',
    'location': 'RER',
    'reference product': 'xylene, mixed',
    'unit': 'kg',
    'allocation': 0.8824247063962822}]}]
```

### Data format

Migration data is specified in a JSON file as a single dictionary. This file **must** include the following keys:

* `name`: Follows the [data package specification](https://specs.frictionlessdata.io/data-package/#name).
* `licenses`: Follows the [data package specification](https://specs.frictionlessdata.io/data-package/#licenses). Must be a list.
* `version`: Follows the [data package specification](https://specs.frictionlessdata.io/data-package/#version). Must be a string.
* `contributors`: Follows the [data package specification](https://specs.frictionlessdata.io/data-package/#contributors). Must be a list.
* `mapping`: A dictionary mapping the labels used in the transformation to data accessors.
* `graph_context`: A list with either the string 'nodes', 'edges', or both 'nodes' and 'edges'. This defines what kinds of objects in the graph should be transformed.

We strongly recommend you provide the following optional attributes:

* `source_id`: An identifier for the source dataset following the [common identifier standard](#common-database-release-identifier-standard). Useful if the source data is specific.
* `target_id`: An identifier for the target dataset following the [common identifier standard](#common-database-release-identifier-standard). Useful if the target data is specific.

The following properties should follow the [data package specification](https://specs.frictionlessdata.io/data-package/) if provided:

* `description`
* `sources`
* `homepage`
* `created`

Finally, at least one change type should be included. The change types are:

* `create`
* `replace`
* `update`
* `delete`
* `disaggregate`

Here are some examples. First, migrating from one ecoinvent biosphere version to another:

```json
{
  "name": "ecoinvent-3.9.1-biosphere-ecoinvent-3.10-biosphere",
  "description": "Data migration file from ecoinvent-3.9.1-biosphere to ecoinvent-3.10-biosphere generated with `ecoinvent_migrate` version 0.2.0",
  "contributors": [
    {
      "title": "ecoinvent association",
      "path": "https://ecoinvent.org/",
      "role": "author"
    },
    {
      "title": "Chris Mutel",
      "path": "https://chris.mutel.org/",
      "role": "wrangler"
    }
  ],
  "created": "2024-07-24T11:38:11.144509+00:00",
  "version": "2.0.0",
  "licenses": [
    {
      "name": "CC-BY-4.0",
      "path": "https://creativecommons.org/licenses/by/4.0/legalcode",
      "title": "Creative Commons Attribution 4.0 International"
    }
  ],
  "graph_context": [
    "edges"
  ],
  "mapping": {
    "source": {
      "expression language": "XPath",
      "labels": {
        "name": "//*:elementaryExchange/*:name/text()",
        "unit": "//*:elementaryExchange/*:unitName/text()",
        "uuid": "//*:elementaryExchange/@elementaryExchangeId"
      }
    },
    "target": {
      "expression language": "XPath",
      "labels": {
        "name": "//*:elementaryExchange/*:name/text()",
        "unit": "//*:elementaryExchange/*:unitName/text()",
        "uuid": "//*:elementaryExchange/@elementaryExchangeId"
      }
    }
  },
  "source_id": "ecoinvent-3.9.1-biosphere",
  "target_id": "ecoinvent-3.10-biosphere",
  "homepage": "https://github.com/brightway-lca/ecoinvent_migrate",
  "replace": [
    {
      "source": {
        "uuid": "90a94ea5-bca4-483d-a591-2e886c0ff47f",
        "name": "TiO2, 54% in ilmenite, 18% in crude ore"
      },
      "target": {
        "uuid": "2f033407-6060-4e1e-868c-9f362d10fdb2",
        "name": "Titanium"
      },
      "conversion_factor": 0.599,
      "comment": "To be modelled as pure elements, the titanium content of titanium dioxide is 0.599."
    }
  ]
}
```

Name, moving from SimaPro to ecoinvent nomenclature:

```json
{
  "name": "simapro-ecoinvent-3.10-cutoff",
  "description": "Data migration file from SimaPro 9 to ecoinvent-3.10-cutoff generated by PRé and provided via request at https://support.simapro.com/s/contactsupport",
  "contributors": [
    {
      "title": "PRé",
      "path": "https://pre-sustainability.com/",
      "role": "author"
    },
    {
      "title": "Chris Mutel",
      "path": "https://chris.mutel.org/",
      "role": "wrangler"
    }
  ],
  "created": "2024-07-24T10:37:28.350572+00:00",
  "version": "2.0.0",
  "licenses": [
    {
      "name": "CC-BY-4.0",
      "path": "https://creativecommons.org/licenses/by/4.0/legalcode",
      "title": "Creative Commons Attribution 4.0 International"
    }
  ],
  "graph_context": [
    "edges"
  ],
  "mapping": {
    "source": {
      "expression language": "like JSONPath",
      "labels": {
        "identifier": "Process[*].\"Process identifier\".text",
        "name": "Process[*].Products[*].text[0]",
        "platform_id": "Process[*].\"Platform Identifier\""
      }
    },
    "target": {
      "expression language": "XPath",
      "labels": {
        "filename": "concat(//*:activity/@id, '_', //*:intermediateExchange[*:outputGroup = '0' and @amount > 0]/@intermediateExchangeId, '.spold')",
        "name": "//*:activityName/text()",
        "location": "//*:geography/*:shortname/text()",
        "reference product": "//*:intermediateExchange[*:outputGroup = '0' and @amount > 0]/*:name/text()",
        "unit": "//*:intermediateExchange[*:outputGroup = '0' and @amount > 0]/*:unitName/text()"
      }
    }
  },
  "source_id": "SimaPro-9",
  "target_id": "ecoinvent-3.10-cutoff",
  "replace": [
    {
      "source": {
        "identifier": "EI3ARUNI000011519620702",
        "name": "Sawnwood, azobe, dried (u=15%), planed {RER}| market for sawnwood, azobe, dried (u=15%), planed | Cut-off, U",
        "platform_id": "FE069A7D-BB64-4A2E-8B1B-12960BE28887"
      },
      "target": {
        "filename": "151e46e9-70f3-58de-80b3-eb79a90036b0_148b552a-c50b-465e-84f7-367bda16f04a.spold",
        "name": "market for sawnwood, azobe, dried (u=15%), planed",
        "location": "RER",
        "reference product": "sawnwood, azobe, dried (u=15%), planed",
        "unit": "m3"
      }
    }
  ]
}
```

Finally, normalizing unit abbreviations to full names:

```json
{
    "name": "generic-brightway-units-normalization",
    "description": "Standard units normalization used in most Brightway projects",
    "contributors": [
        {"title": "Chris Mutel", "path": "https://chris.mutel.org/", "role": "author"}
    ],
    "created": "2024-07-25T06:47:10.575370+00:00",
    "version": "1.0.0",
    "licenses": [
        {
            "name": "CC-BY-4.0",
            "path": "https://creativecommons.org/licenses/by/4.0/legalcode",
            "title": "Creative Commons Attribution 4.0 International",
        }
    ],
    "graph_context": ["nodes", "edges"],
    "mapping": {
        "source": {"expression language": "JSONPath", "labels": {"unit": "Node.unit"}},
        "target": {"expression language": "JSONPath", "labels": {"unit": "Node.unit"}},
    },
    "source_id": "bw_interfaces_schemas-1",
    "target_id": "bw_interfaces_schemas-1",
    "homepage": "https://github.com/brightway-lca/bw_interface_schemas",
    "replace": [
        {"source": {"unit": "a"}, "target": {"unit": "year"}},
        {"source": {"unit": "h"}, "target": {"unit": "hour"}},
        {"source": {"unit": "ha"}, "target": {"unit": "hectare"}},
        {"source": {"unit": "hr"}, "target": {"unit": "hour"}},
        {"source": {"unit": "kg"}, "target": {"unit": "kilogram"}},
    ],
}
```

See the [randonneur_data](https://github.com/brightway-lca/randonneur_data) repo for more real-world implementations.

### Common database release identifier standard

At Brightcon 2022 we developed the following simple format for common database release identifiers:

`<database name>-<version>-<optional modifier>`

`database name` is usually lower case.

Here are some examples:

* `agribalyse-3.1.1`
* `forwast-1`
* `ecoinvent-3.10-cutoff`
* `simapro-9-biosphere`

## Theory

In normal life cycle assessment practice, we work with a large variety of software and database applications, and often need to harmonize data across these heterogeneous systems. Because many of these systems do not commonly use simple and unique identifiers, we often need to link across systems based on data attibutes. For example, if the name, location, and unit of an input are the same in system `A` and `B`, then we can infer that these refer to the same underlying concept.

In the real world it's not so simple. Each player in the LCA data world is trying to give their users a positive experience, but over time this has led to many different terms for the same concept. Some legacy systems restrictions also prevent complete imports, and cause data transformations that are difficult to reverse engineer.

This library defines both a specification for transformation data files which allow different systems to be linked together by harmonizing the matching attributes, and a software-agnostic reference implementation of functions needed to use that format.

Note that *not all verbs or graph object types* are currently supported by the reference implmentation.

## Transformations

> [!NOTE]
> Transformations are serialized to JSON. Therefore, only [JSON data types](https://en.wikipedia.org/wiki/JSON) are supported.

### Configuration

All transformation operations can be configured via a `MigrationConfig` object. The following can be specified:

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

If you changed labels in `mapping`, use the changed labels, not the original key labels.

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

### Replace and Update

> [!WARNING]
> Be careful with nested data. The reference implementation takes a relatively simplistic approach, and completely overwrites existing data if a new `target` value is provided. If you had `{'foo': {'nested': {'has_permission': true, 'author': 'someone'}}}`, and the transformation gave a new value for `nested`, it would completely replace the `nested` dictionary instead of modifying the existing and  adding new elements.

`replace` indicates that a given object should be replaced with a new object. The replacement could substitutes an object one-to-one; as such, the new exchange must be completely defined. Please bear in mind that we are providing transformations for the object that the edge is referring to, not the edge itself. Therefore, the `amount`, uncertainty, etc. of the edge should not be specified. It the edge amount needs to be rescaled, for example because of a unit conversion, specify a `conversion_factor` in addition to the `source` and `target`.

If `allocation` is not given, a default value of 1.0 is used.

Aside from the quantitative values, no other data from the original exchange is taken over to the new exchange. If you only want to change a few fields, use an `update` instead. If you don't want the exchange amount re-scaled, use a combination of `delete` and `create`.

The data format for `replace` type is:

```python
{
    "replace": [{
        "source": {
            # All fields needed to identify the exchange to be replaced
        },
        "target": {
            # All fields needed to define the new exchange
        }
    }]
}
```

`update` changes attributes the same way that `replace` does - the only difference is that `replace` shows the intent to refer to a new object instead of an existing object with different attributes. Given the messiness of real-world data (i.e. what is truly a new object versus the same object with different descriptions), there is no real bright line between these concepts, and their code implementation is identical.

### Create

Creates a new edge or node.

> [!NOTE]
> Because this application pattern is so different compared to updating existing values, we don't normally recommend using this functionality. It's preferable to go through the normal data importation process instead.

> [!NOTE]
> The reference implementation does not check if creation would create multiple identical objects, and the `randonneur` specification does not define what should be done if such creation were indicated.

Because we are specifying a new node or exchange, we need to list **all** information needed to define that object, **including** the edges and edge `amount` values. This is different than the other modification types, where *relative* amounts are given with the key `conversion_factor` or `allocation`. We can't give relative amounts here because we have no edge to refer to, and we don't have a surefire way to identify the reference production edge (and there might not be one in any case).

If you want to add an edge to all datasets, or a node to the graph:

```python
{
    "create": [{
        "target": {
            # All fields needed to define the object
        }
    }]
}
```

To add multiple nodes or edges, add multiple `{'target': {}}` dictionaries to the `create` list.

### Delete

Delete exchanges. Follows the same patterns as `replace` and `update`:

```python
{
    "delete": [{
        "source": {
            # All fields needed to identify the exchange to be deleted
        }
    }]
}
```

### Disaggregate

Disaggregation is splitting one exchange into many. The `allocation` field is used to determine how much of the exchange passes to each new exchange.

> [!NOTE]
> `allocation` fields do not have to sum to one.

The new exchanges start as **copies** of the original exchange, and are updating using the additional data provided.

The data format includes a list of new exchanges for each matched source:

```python
{
    "disaggregate": [{
        "source": {
            # All fields needed to identify the exchange to be disaggregated
        },
        "targets": [{
            # Some fields which you want to change
        }]
    }]
}
```

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license], `randonneur` is free and open source software.

## Issues

If you encounter any problems,
please [file an issue](https://github.com/cmutel/randonneur/issues/new/choose) along with a detailed description.

<!-- github-only -->

[license]: https://github.com/brightway-lca/randonneur/blob/main/LICENSE
[contributor guide]: https://github.com/brightway-lca/randonneur/blob/main/CONTRIBUTING.md
