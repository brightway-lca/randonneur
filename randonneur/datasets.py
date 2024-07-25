from copy import deepcopy

from tqdm import tqdm

from .utils import matcher


def migrate_datasets(
    migration_data,
    lci_database,
    create=True,
    disaggregate=True,
    replace=True,
    update=True,
    delete=True,
    dataset_filter=None,
    verbose=False,
    only_one_change=True,
):
    """Migrate datasets from ``lci_database`` using the data in ``migration_data``.

    ``create``, ``disaggregate``, ``replace``, ``update``, and ``delete`` changes can be applied,
    and their activation is controlled by their respective flags. See the README for more detail
    on the specifics of these changes, and the data formats of ``migration_data`` and
    ``lci_database``.

    You can filter the datasets to be changed with ``dataset_filter``. If given, these should be
    callables that take a dataset as the single input argument, and return a ``True`` if changes
    should be made.

    ``verbose`` controls whether a progressbar is shown when iterating over ``lci_database``.

    ``only_one_change`` determines whether more than one change (either of multiple types, or of
    the same type if multiple changes which match the original exchange are given) is executed. Be
    very careful with this, many changes to large databases should be carefully checked.

    Returns ``lci_database`` with altered content.
    """
    progressbar = tqdm if verbose else lambda x: iter(x)

    datasets_to_delete = []
    datasets_to_add = migration_data.get("create-datasets", []) if create else []

    for dataset in progressbar(lci_database):
        found = False

        if dataset_filter is not None and not dataset_filter(dataset):
            continue

        for possible in migration_data.get("delete", []):
            if not (found and only_one_change) and matcher(possible, dataset):
                datasets_to_delete.append(dataset)
                found = True

        for possible in migration_data.get("replace", []):
            if not (found and only_one_change) and matcher(possible["source"], dataset):
                datasets_to_add.append(deepcopy(possible["target"]))
                datasets_to_delete.append(dataset)
                found = True

        for possible in migration_data.get("update", []):
            if not (found and only_one_change) and matcher(possible["source"], dataset):
                dataset.update(possible["target"])
                found = True

        for possibles in migration_data.get("disaggregate", []):
            if not (found and only_one_change) and matcher(possibles["source"], dataset):
                for new_ds in possibles["targets"]:
                    old_ds = deepcopy(dataset)
                    old_ds.update(new_ds)
                    datasets_to_add.append(old_ds)
                datasets_to_delete.append(dataset)
                found = True

    if datasets_to_delete:
        lci_database = [dataset for dataset in lci_database if dataset not in datasets_to_delete]
    if datasets_to_add:
        lci_database.extend(datasets_to_add)

    return lci_database
