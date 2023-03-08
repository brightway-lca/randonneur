from tqdm import tqdm
from functools import partial
from copy import copy


def as_tuple(obj, fields):
    def converter(value):
        if isinstance(value, list):
            return tuple(value)
        else:
            return value

    return tuple([converter(obj.get(field)) for field in fields])


def migrate_exchanges(
    migration_data,
    lci_database,
    create=True,
    disaggregate=True,
    replace=True,
    update=True,
    delete=True,
    node_filter=None,
    exchange_filter=None,
    fields=("name", "reference product", "product", "location", "unit"),
    verbose=False,
):
    """Migrate the exchanges (sometimes called exchanges) in the datasets given in ``lci_database`` using the data in ``migration_data``.

    The types of changes applied are controlled by the input flags ``create``, ``disaggregate``, ``replace``, and ``delete``. See the readme for more detail on these changes.

    You can filter the nodes to be changed, and the exchanges to consider, with the filters ``node_filter`` and ``exchange_filter``. Both should be ``None`` or a callable, and take the complete activity dataset or a single exchange dataset as an input. The filters are applied **only to the original exchange data**; as such, they only apply to ``disaggregate``, ``replace``, and ``delete``.

    Returns ``lci_database`` with altered content.

    """
    mapping_key = partial(as_tuple, fields=sorted(fields))

    if verbose:
        print("Preparing mappings from `migration_data`")
        progressbar = tqdm
    else:
        progressbar = lambda x: iter(x)

    try:
        deletion_generic_mapping = {
            mapping_key(obj["source"])
            for obj in migration_data["delete"]
            if "node" not in obj
        }
        deletion_specific_mapping = {
            (mapping_key(obj["source"]), mapping_key(obj["node"]))
            for obj in migration_data.get("delete", [])
            if "node" in obj
        }

        replacement_generic_mapping = {
            mapping_key(obj["source"]): obj["target"]
            for obj in migration_data.get("replace", [])
            if "node" not in obj
        }
        replacement_specific_mapping = {
            (mapping_key(obj["source"]), mapping_key(obj["node"])): obj["target"]
            for obj in migration_data.get("replace", [])
            if "node" in obj
        }

        update_generic_mapping = {
            mapping_key(obj["source"]): obj["target"]
            for obj in migration_data.get("update", [])
            if "node" not in obj
        }
        update_specific_mapping = {
            (mapping_key(obj["source"]), mapping_key(obj["node"])): obj["target"]
            for obj in migration_data.get("update", [])
            if "node" in obj
        }

        create_generic_mapping = [
            obj["target"]
            for obj in migration_data.get("create", [])
            if "node" not in obj
        ]
        create_specific_mapping = {
            mapping_key(obj["node"]): obj["target"]
            for obj in migration_data.get("create", [])
            if "node" in obj
        }

        # disaggregation_mapping = {}
    except TypeError as exc:
        ERROR = (
            "Couldn't cast input data to a hashable type, please use fields"
            " with only strings and tuples"
        )
        raise ValueError(ERROR) from exc

    for dataset in progressbar(lci_database):
        if node_filter is not None and not node_filter(dataset):
            continue

        exchanges_to_delete = []
        exchanges_to_add = []
        exchanges = dataset.get("exchanges", [])
        node_key = mapping_key(dataset)

        for exchange in exchanges:
            if exchange_filter is not None and not exchange_filter(exchange):
                continue

            exchange_key = mapping_key(exchange)
            if (
                delete
                and (exchange_key in deletion_generic_mapping)
                or ((exchange_key, node_key) in deletion_specific_mapping)
            ):
                exchanges_to_delete.append(exchange)
            elif replace:
                if exchange_key in replacement_generic_mapping:
                    new_exchange = copy(replacement_generic_mapping[exchange_key])
                    new_exchange["amount"] *= new_exchange.pop("allocation", 1.0)
                    exchanges_to_add.append(new_exchange)
                    exchanges_to_delete.append(exchange)
                elif (exchange_key, node_key) in replacement_specific_mapping:
                    new_exchange = copy(
                        replacement_specific_mapping[(exchange_key, node_key)]
                    )
                    new_exchange["amount"] *= new_exchange.pop("allocation", 1.0)
                    exchanges_to_add.append(new_exchange)
                    exchanges_to_delete.append(exchange)
            elif update:
                if exchange_key in update_generic_mapping:
                    new_exchange = update_generic_mapping[exchange_key]
                    exchange["amount"] *= new_exchange.pop("allocation", 1.0)
                    exchange.update(new_exchange)
                elif (exchange_key, node_key) in update_specific_mapping:
                    new_exchange = update_specific_mapping[(exchange_key, node_key)]
                    exchange["amount"] *= new_exchange.pop("allocation", 1.0)
                    exchange.update(new_exchange)

            # elif disaggregate and key in disaggregation_mapping:
            #     exchanges_to_delete.append(exchange)
            #     for other_exchange in disaggregation_mapping[key]:
            #         new_exchange = copy(exchange)
            #         new_exchange['amount'] *= other_exchange.pop("allocation", 1.0)
            #         new_exchange.update(other_exchange)

        if create:
            exchanges_to_add.extend(create_generic_mapping)
            try:
                exchanges_to_add.extend(create_specific_mapping[node_key])
            except KeyError:
                pass

        if exchanges_to_delete:
            exchanges = [
                exchange
                for exchange in exchanges
                if exchange not in exchanges_to_delete
            ]
        if exchanges_to_add:
            exchanges.extend(exchanges_to_add)
        dataset["exchanges"] = exchanges
    return lci_database
