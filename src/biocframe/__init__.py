from sys import version_info

if version_info[:2] >= (3, 8):
    from importlib.metadata import (  # type: ignore
        PackageNotFoundError,  # type: ignore
        version,  # type: ignore
    )
else:
    from importlib_metadata import (
        PackageNotFoundError,  # type: ignore
        version,  # type: ignore
    )

try:
    __version__: str = version(__name__.rsplit(".", 1)[0])  # type: ignore
except PackageNotFoundError:  # pragma: no cover
    __version__: str = "unknown"
finally:
    del version, PackageNotFoundError

from .BiocFrame import BiocFrame as BiocFrame
from .io import from_pandas as from_pandas
