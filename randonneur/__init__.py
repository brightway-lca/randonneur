"""randonneur."""
from randonneur.utils import get_version_tuple

__all__ = (
    "__version__",
    "migrate_exchanges",
    # Add functions and variables you want exposed in `randonneur.` namespace here
)

__version__ = get_version_tuple()

from .exchanges import migrate_exchanges
