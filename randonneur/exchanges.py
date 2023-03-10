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

    The types of changes applied are controlled by the input flags ``create``, ``disaggregate``,
    ``replace``, ``update``, and ``delete``. See the README for more detail on these changes.

    You can filter the datasets to be changed, and the exchanges to consider, with the filters
    ``dataset_filter`` and ``exchange_filter``. This filters control _if_ a dataset or exchange
    should be modified (i.e. it is modified if the function returns ``True``). If given, they
    should be a callable, and take the complete activity dataset or a single exchange dataset as an
    input.

    You can specify the fields used to test for equality between exchange and exchange, or dataset
    and dataset. Be careful, if you specify a field missing in both the ``migration_data`` and the
    ``lci_database``, the equality condition will match.

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
                        new_exchange = deepcopy(possible)
                        new_exchange["amount"] = exchange["amount"] * new_exchange.pop(
                            "allocation", 1.0
                        )
                        exchanges_to_add.append(new_exchange)
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
