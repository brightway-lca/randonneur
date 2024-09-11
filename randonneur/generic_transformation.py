from functools import partial
from typing import Callable, Dict, List, Optional

from loguru import logger
from tqdm import tqdm

from randonneur.config import MigrationConfig
from randonneur.utils import FlexibleLookupDict, apply_mapping


def generic_transformation(
    graph: List[dict],
    migrations: dict,
    verb_dispatch: Dict[str, Callable],
    is_edges: bool = True,
    config: Optional[MigrationConfig] = None,
) -> List[dict]:
    config = config or MigrationConfig()
    label = "edges" if is_edges else "nodes"
    progressbar = (
        partial(tqdm, desc=f"Transforming graph {label}") if config.verbose else lambda x: iter(x)
    )

    if config.mapping:
        migrations = apply_mapping(
            migrations=migrations, mapping=config.mapping, verbs=config.verbs
        )

    verbs = list(filter(lambda x: x in verb_dispatch and x in migrations, config.verbs))
    logger.info("Can apply the following transformation verbs: {v}", v=verbs)

    flds = {
        verb: FlexibleLookupDict(
            input_data=migrations[verb],
            fields_filter=config.fields,
            case_sensitive=config.case_sensitive,
        )
        for verb in verbs
        if verb != "create"
    }

    if is_edges and "create" in migrations and "create" in verbs and not config.node_filter:
        logger.warning(
            """
`migrations` has `create` section.
No `node_filter` is configured, meaning that these nodes will be added to all nodes.
This is almost never the desired behaviour, consider removing `create` from the `verb` input.
        """
        )
    if "create" in migrations and "create" in verbs:
        flds["create"] = migrations["create"]

    if is_edges:
        for node in progressbar(graph):
            if config.node_filter and not config.node_filter(node):
                continue

            for verb in verbs:
                verb_dispatch[verb](
                    node=node,
                    migration_fld=flds[verb],
                    config=config,
                )
    else:
        for verb in progressbar(verbs):
            verb_dispatch[verb](
                graph=graph,
                migration_fld=flds[verb],
                config=config,
            )
    return graph
