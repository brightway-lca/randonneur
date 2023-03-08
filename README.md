# randonneur

<img src="randonneur.jpg" alt="https://www.flickr.com/photos/jswg/35681111281/">

Keep moving forward.

Randonneur is a library to make broad or specific changes to life cycle inventory databases. You can use it to re-link your data to the latest version of a background database, to update existing databases with new data, or to perform other data changes. Randonneur uses JSON files to describe these changes; contrast this with [wurst](https://github.com/polca/wurst), which can do these manipulations and more, but describes its manipulations in code.

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

`randonneur` supports two migration functions, each with their own migration data format.

All input functions take data in the [`wurst` format](https://wurst.readthedocs.io/#internal-data-format).

### Migrating exchanges

Exchanges are the consumption or production of a good or service. Exchanges link two nodes (two activities, one product and one activity, one activity and one biosphere flow, or even other node types). We support the following types of exchange changes:

* Create
* Replace
* Update
* Delete
* Disaggregate

#### Generic data format

Exchange migration is specified in a JSON file. This file should include information on the data author and license (following the datapackage conventions), and at least one of the migration types: `create`, `replace`, `update`, `delete`, and `disaggregate`. None of the types are required.

#### Create

Creates a new exchange in all nodes, or in one specific node.

Because we are specifying a new exchange, we need to list **all** information needed to define an exchange, **including** the exchange `amount`. This is different than the other modification types, where *relative* amounts are given with the key `allocation`. We can't give relative amounts here because we have no exchange to refer to, and we don't have a surefire way to identify the reference production exchange (and there might not be one in any case).

If you want to add an exchange to all nodes:

```python
{
    "create": [{
        "targets": [{
            # All fields needed to define an exchange
        }]
    }]
}
```

If you only want to create an exchange in one node:

```python
{
    "create": [{
        "targets": [{
            # All fields needed to define an exchange
        }],
        "node": {
            # All fields needed to identify the node
        }
    }]
}
```

`node` must be a `dict`, not a list; it can only identify one node.

Note that in the `wurst` format, `node` use the key `reference product` while exchanges use the key `product`; these are two different concepts, so have different keys.

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
        # `node` is optional
        "node": {
            # All fields needed to identify the node to change
        }
    }]
}
```

### Update

`update` differs from `replace` in that it changes attributes of the original exchange instead of creating a new object; otherwise, its behaviour is the same as `replace`. The data format is:

```python
{
    "update": [{
        "source": {
            # All fields needed to identify the exchange to be modified
        },
        "target": {
            # Some fields which you want to change
        },
        # `node` is optional
        "node": {
            # All fields needed to identify the node to change
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
        # `node` is optional
        "node": {
            # All fields needed to identify the node to change
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
        # `node` is optional
        "node": {
            # All fields needed to identify the node to change
        }
    }]
}
```

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [BSD 3 Clause license][license],
_randonneur_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue](https://github.com/cmutel/randonneur/issues/new/choose) along with a detailed description.


<!-- github-only -->

[command-line reference]: https://randonneur.readthedocs.io/en/latest/usage.html
[license]: https://github.com/brightway-lca/randonneur/blob/main/LICENSE
[contributor guide]: https://github.com/brightway-lca/randonneur/blob/main/CONTRIBUTING.md
