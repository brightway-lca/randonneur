__all__ = (
    "__version__",
    "migrate_exchanges",
)

from randonneur.utils import get_version_tuple

__version__ = get_version_tuple()

from .exchanges import migrate_exchanges
