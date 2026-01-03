from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas

from ..BiocFrame import BiocFrame

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def from_pandas(input: "pandas.DataFrame") -> BiocFrame:
    """Alias for the :py:meth:`~biocframe.BiocFrame.BiocFrame.from_pandas` method, provided for back-compatibility
    only."""
    return BiocFrame.from_pandas(input)
