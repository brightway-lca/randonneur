from copy import deepcopy

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

from frozendict import frozendict

from .utils import matcher, maybe_filter


def migrate_exchanges(
    migration_data,
    lci_database,
    create=True,
    disaggregate=True,
    replace=True,
    update=True,
    delete=True,
    dataset_filter=None,
    exchange_filter=None,
    verbose=False,
    only_one_change=True,
):
    """Migrate the exchanges in the datasets given in ``lci_database`` using the data in
    ``migration_data``.

    ``create``, ``disaggregate``, ``replace``, ``update``, and ``delete`` changes can be applied,
    and their activation is controlled by their respective flags. See the README for more detail
    on the specifics of these changes, and the data formats of ``migration_data`` and
    ``lci_database``.

    You can filter the datasets and exchanges to be changed with ``dataset_filter`` and
    ``exchange_filter``. If given, these should be callables that take a dataset or exchange as
    the single input argument, and return a ``True`` if changes should be made.

    ``verbose`` controls whether a progressbar is shown when iterating over ``lci_database``.

    ``only_one_change`` determines whether more than one change (either of multiple types, or of
    the same type if multiple changes which match the original exchange are given) is executed. Be
    very careful with this, many changes to large databases should be carefully checked.

    Returns ``lci_database`` with altered content.

    """
    if verbose and tqdm:
        progressbar = tqdm
    else:
        progressbar = lambda x: iter(x)  # noqa: E731

    for dataset in progressbar(lci_database):
        if dataset_filter is not None and not dataset_filter(dataset):
            continue

        exchanges_to_delete = set()
        exchanges_to_add = [
            obj["source"]
            for obj in migration_data.get("create-exchanges", [])
            if matcher(obj["dataset"], dataset)
        ]
        exchanges = dataset.get("exchanges", [])

        for exchange in exchanges:
            found = False

            if exchange_filter is not None and not exchange_filter(exchange):
                continue

            for possible in migration_data.get("delete", []):
                if (
                    not (found and only_one_change)
                    and matcher(possible, exchange)
                    and maybe_filter(possible.get("dataset"), dataset)
                ):
                    exchanges_to_delete.add(frozendict(exchange))
                    found = True

            for possible in migration_data.get("replace", []):
                if (
                    not (found and only_one_change)
                    and matcher(possible["source"], exchange)
                    and maybe_filter(possible.get("dataset"), dataset)
                ):
                    new_exchange = deepcopy(possible["target"])
                    # TBD: rescale uncertainty
                    new_exchange["amount"] = exchange["amount"] * new_exchange.pop(
                        "allocation", 1.0
                    )
                    exchanges_to_add.append(new_exchange)
                    exchanges_to_delete.add(frozendict(exchange))
                    found = True

            for possible in migration_data.get("update", []):
                if (
                    not (found and only_one_change)
                    and matcher(possible["source"], exchange)
                    and maybe_filter(possible.get("dataset"), dataset)
                ):
                    new_values = deepcopy(possible["target"])
                    exchange["amount"] *= new_values.pop("allocation", 1.0)
                    exchange.update(new_values)
                    found = True

            for possibles in migration_data.get("disaggregate", []):
                if (
                    not (found and only_one_change)
                    and matcher(possibles["source"], exchange)
                    and maybe_filter(possibles.get("dataset"), dataset)
                ):
                    for possible in possibles["targets"]:
                        base_exchange, new_exchange = deepcopy(exchange), deepcopy(
                            possible
                        )
                        base_exchange["amount"] = base_exchange[
                            "amount"
                        ] * new_exchange.pop("allocation", 1.0)
                        base_exchange.update(new_exchange)
                        exchanges_to_add.append(base_exchange)
                    exchanges_to_delete.add(frozendict(exchange))
                    found = True

        if exchanges_to_delete:
            exchanges = [
                exchange
                for exchange in exchanges
                if frozendict(exchange) not in exchanges_to_delete
            ]
        if exchanges_to_add:
            exchanges.extend(exchanges_to_add)
        dataset["exchanges"] = exchanges
    return lci_database
