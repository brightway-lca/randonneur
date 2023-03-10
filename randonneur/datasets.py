from copy import deepcopy

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None

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

    The types of changes applied are controlled by the input flags ``create``,
    ``disaggregate``, ``replace``, ``update``, and ``delete``. See the README for
    more detail on these changes.

    You can filter the datasets to be changed with the filter ``dataset_filter``.
    This filter controls _if_ a dataset should be modified (i.e. it is modified if
    the function returns ``True``). This function takes the dataset as in input
    argument.

    Returns ``lci_database`` with altered content.

    """
    if verbose and tqdm:
        print("Preparing mappings from `migration_data`")
        progressbar = tqdm
    else:
        progressbar = lambda x: iter(x)  # noqa: E731

    # TBD: Old semantics based on mappings; make nicer

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
            if not (found and only_one_change) and matcher(
                possibles["source"], dataset
            ):
                for new_ds in possibles["targets"]:
                    old_ds = deepcopy(dataset)
                    old_ds.update(new_ds)
                    datasets_to_add.append(old_ds)
                datasets_to_delete.append(dataset)
                found = True

    if datasets_to_delete:
        lci_database = [
            dataset for dataset in lci_database if dataset not in datasets_to_delete
        ]
    if datasets_to_add:
        lci_database.extend(datasets_to_add)

    return lci_database
