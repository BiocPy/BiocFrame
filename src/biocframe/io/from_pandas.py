"""A function for converting from pandas.DataFrame to BiocFrame."""

from typing import Any, Dict, List, Optional

from ..BiocFrame import BiocFrame

try:
    from pandas import DataFrame, RangeIndex
except Exception:
    pass

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def from_pandas(df: "DataFrame") -> "BiocFrame":
    """Read a :py:class:`~biocframe.BiocFrame.BiocFrame` from :py:class:`~pandas.DataFrame` object.

    Args:
        df (:py:class:`~pandas.DataFrame`): Input data.

    Raises:
        TypeError: If ``input`` is not a :py:class:`~pandas.DataFrame`.

    Returns:
        BiocFrame: A :py:class:`~biocframe.BiocFrame.BiocFrame` object.
    """
    r_data: Dict[str, List[Any]] = df.to_dict("list")  # type: ignore
    r_index: Optional[List[str]] = None

    if df.index is not RangeIndex:  # type: ignore
        r_index = df.index.to_list()  # type: ignore

    return BiocFrame(data=r_data, row_names=r_index)
