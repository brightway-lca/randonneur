# randonneur

<img src="randonneur.jpg" alt="https://www.flickr.com/photos/jswg/35681111281/">

Keep moving forward.

Randonneur is a library to make changes to life cycle inventory databases. You can use it to re-link your data to the latest version of a background database, to update existing databases with new data, or to perform other data transformations. Randonneur uses JSON files to describe these changes; contrast this with [wurst](https://github.com/polca/wurst), which can do these manipulations and more, but documents its manipulations in code.

Although designed to work with [Brightway](https://brightway.dev/), this library is not Brightway-specific.

[![PyPI](https://img.shields.io/pypi/v/randonneur.svg)][pypi status]
[![Status](https://img.shields.io/pypi/status/randonneur.svg)][pypi status]
[![Python Version](https://img.shields.io/pypi/pyversions/randonneur)][pypi status]
[![License](https://img.shields.io/pypi/l/randonneur)][license]

[![Tests](https://github.com/brightway-lca/randonneur/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/brightway-lca/randonneur/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi status]: https://pypi.org/project/randonneur/
[tests]: https://github.com/brightway-lca/randonneur/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/brightway-lca/randonneur
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Usage

### Generic usage pattern

* Load a `randonneur` data migration file, normally from [randonneur_data](https://github.com/brightway-lca/randonneur_data) using `randonneur_data.Registry().get_file()`
* Load an inventory database, normally in the [common Brightway inventory format](https://github.com/brightway-lca/bw_interface_schemas)
* Apply the data transformation using either `migrate_edges` or `migrate_nodes`, optionally specifying the fields used for matching the transformation data, any mappings necessary to make the transformation data schema fit into your data schema, what filters should be applied to the input data (if any), and which verbs (`create`, `replace`, `update`, `delete`, or `disaggregate`) you want to apply
* Save the modified data

### Data format

Migration data is specified in a JSON file as a single dictionary. This file **must** include the following keys:

* `name`: Follows the [data package specification](https://specs.frictionlessdata.io/data-package/#name).
* `licenses`: Follows the [data package specification](https://specs.frictionlessdata.io/data-package/#licenses). Must be a list.
* `version`: Follows the [data package specification](https://specs.frictionlessdata.io/data-package/#version). Must be a string.
* `contributors`: Follows the [data package specification](https://specs.frictionlessdata.io/data-package/#contributors). Must be a list.
* `mapping`: A dictionary mapping the labels used in the transformation
* `graph_context`: A list with either the string 'nodes', 'edges', or both.

In addition, the following properties should follow the [data package specification](https://specs.frictionlessdata.io/data-package/) if provided:

* `description`
* `sources`
* `homepage`
* `created`

You can specify the following optional attributes:

* `source_id`: An identifier for the source dataset following the [common identifier standard](#common-database-release-identifier-standard). Useful if the source data is specific.
* `target_id`: An identifier for the target dataset following the [common identifier standard](#common-database-release-identifier-standard). Useful if the target data is specific.

Finally, at least one change type should be included. The change types are:

* `create`
* `replace`
* `update`
* `delete`
* `disaggregate`

Here are two examples:
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
      "name": "CC BY 4.0",
      "path": "https://creativecommons.org/licenses/by/4.0/",
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
      "allocation": 0.599,
      "comment": "To be modelled as pure elements, the titanium content of titanium dioxide is 0.599."
    }
  ]
}
```

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
      "name": "CC BY 4.0",
      "path": "https://creativecommons.org/licenses/by/4.0/",
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

You can use `randonneur.Datapackage` to ensure correct formatting and serialization.

See the directory `examples` for more real-world implementations.

### Common database release identifier standard

At Brightcon 2022 we developed the following simple format for common database release identifiers:

`<database name>-<version>-<optional modifier>`

Here are some examples:

* `agribalyse-3.1.1`
* `forwast-1`
* `ecoinvent-3.10-cutoff`
* `SimaPro-9-biosphere`

## Theory

For migrating exchanges: Given a database, iterate through the datasets. If a `dataset_filter` is given, ignore any datasets which don't pass the filter. In each dataset, iterate through the exchanges. If an `exchange_filter` is given, ignore any exchanges which don't pass the filter. For each exchange, look at the following possible transformations in order: `delete`, `replace`, `update`, and `disaggregate`. Only one transformation can be done to an exchange. Each transformation will change or delete the exchange under consideration, and maybe add some new exchanges to the dataset, though this addition will only happen after the original exchanges have been examined. After looking at all the exchanges, apply the `create` transformation to add more exchanges if provided.

For each exchange and transformation, we need to decide if that transformation should be applied. We do this based on the attributes of the dataset and exchange, and the attributes given in the transformation data. We compare the attribute values for a given set of fields, and these attributes must match exactly. The default fields are `name`, `reference product`, `product`, `location`, `unit`; you can specify your own fields.

Migrating datasets works the same way, except that we operate directly on the datasets instead of the exchanges.

### Migrating exchanges

Exchanges are the consumption or production of a good or service. Exchanges link two datasets (two activities, one product and one activity, one activity and one biosphere flow, or even other dataset types). We support the following types of exchange changes:

* `delete`
* `replace`
* `update`
* `disaggregate`
* `create`

#### Create

Creates a new exchange in all datasets, or in one specific dataset.

Because we are specifying a new exchange, we need to list **all** information needed to define an exchange, **including** the exchange `amount`. This is different than the other modification types, where *relative* amounts are given with the key `allocation`. We can't give relative amounts here because we have no exchange to refer to, and we don't have a surefire way to identify the reference production exchange (and there might not be one in any case).

If you want to add an exchange to all datasets:

```python
{
    "create": [{
        "targets": [{
            # All fields needed to define an exchange
        }]
    }]
}
```

If you only want to create an exchange in one dataset:

```python
{
    "create": [{
        "targets": [{
            # All fields needed to define an exchange
        }],
        "dataset": {
            # All fields needed to identify the dataset
        }
    }]
}
```

`dataset` must be a `dict`, not a list; it can only identify one dataset.

Note that in the `wurst` format, `dataset` use the key `reference product` while exchanges use the key `product`; these are two different concepts, so have different keys.

### Replace

Replacement substitutes an exchange one-to-one; as such, the new exchange must be completely defined. **However**, the `amount` should not be specified; rather, an `allocation` factor should be given, and the `amount` of the original exchange will be multiplied by `allocation`.

If `allocation` is not given, a default value of 1.0 is used.

**Note**: `randonneur` currently does not adjust uncertainty when rescaling.

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
        },
        # `dataset` is optional
        "dataset": {
            # All fields needed to identify the dataset to change
        }
    }]
}
```

### Update

`update` differs from `replace` in that it changes attributes of the original exchange instead of creating a completely new object; otherwise, its behaviour is the same as `replace`. The data format is:

```python
{
    "update": [{
        "source": {
            # All fields needed to identify the exchange to be modified
        },
        "target": {
            # Some fields which you want to change
        },
        # `dataset` is optional
        "dataset": {
            # All fields needed to identify the dataset to change
        }
    }]
}
```

### Delete

Delete exchanges. Follows the same patterns as `replace` and `update`:

```python
{
    "delete": [{
        "source": {
            # All fields needed to identify the exchange to be deleted
        },
        # `dataset` is optional
        "dataset": {
            # All fields needed to identify the dataset to change
        }
    }]
}
```

### Disaggregate

Disaggregation is splitting one exchange into many. The `allocation` field is used to determine how much of the exchange passes to each new exchange.

The new exchanges start as **copies** of the original exchange, and are updating using the additional data provided. In other words, this functions more like an `update` than a `replace`. This is because the most common use case for disaggregation is to split one input or output among several regions, where almost all metadata for the child exchanges would be identical.

`allocation` fields do not have to sum to one.

The data format includes a list of new exchanges for each matched source:

```python
{
    "disaggregate": [{
        "source": {
            # All fields needed to identify the exchange to be disaggregated
        },
        "targets": [{
            # Some fields which you want to change
        }],
        # `dataset` is optional
        "dataset": {
            # All fields needed to identify the dataset to change
        }
    }]
}
```

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [BSD 3 Clause license][license],
`randonneur` is free and open source software.

## Issues

If you encounter any problems,
please [file an issue](https://github.com/cmutel/randonneur/issues/new/choose) along with a detailed description.


<!-- github-only -->

[license]: https://github.com/brightway-lca/randonneur/blob/main/LICENSE
[contributor guide]: https://github.com/brightway-lca/randonneur/blob/main/CONTRIBUTING.md
