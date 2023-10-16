from typing import Any, List, Tuple, Union
from warnings import warn

from biocutils import is_list_of_type

from .types import SlicerTypes

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def _match_to_indices(
    data: Any, query: SlicerTypes
) -> Tuple[Union[slice, List[int]], bool]:
    """Utility function to ingest slicer arguments .

    Args:
        data (List): Input data array to slice.
        query (SlicerTypes): Either a slice or
            a list of indices to keep.

    Returns:
        Tuple[Union[slice, List[int]], bool]: Resolved list of indices and if its a unary slice.
    """

    resolved_indices = None
    is_scalar = False

    if isinstance(query, str):
        resolved_indices = [data.index(query)]
        is_scalar = True
    elif isinstance(query, int):
        if abs(query) > len(data):
            raise ValueError("Integer index is greater than the shape.")
        resolved_indices = [query]
        is_scalar = True
    elif isinstance(query, slice):
        # resolved_indices = list(range(len(data))[query])
        resolved_indices = query
    elif isinstance(query, list) or isinstance(query, tuple):
        if is_list_of_type(query, bool):
            if len(query) != len(data):
                warn(
                    "`indices` is a boolean vector, length should match the size of the data."
                )

            resolved_indices = [i for i in range(len(query)) if query[i] is True]
        elif is_list_of_type(query, int):
            resolved_indices = query
        elif is_list_of_type(query, str):
            diff = list(set(query).difference(set(data)))
            if len(diff) > 0:
                raise ValueError(
                    "`indices` is a string vector, not all values are present in data."
                )

            resolved_indices = [data.index(i) for i in query]
        else:
            raise TypeError("`indices` is a list of unsupported types!")
    else:
        raise TypeError("`indices` is unsupported!")

    return resolved_indices, is_scalar


def _slice_or_index(data: Any, query: Union[slice, List[int]]):
    sliced_data = None
    if isinstance(query, slice):
        sliced_data = data[query]
    elif isinstance(query, list):
        if not isinstance(data, list):
            try:
                return data[query]
            except Exception:
                pass

        sliced_data = [data[i] for i in query]
    else:
        raise TypeError("Cannot match column indices to a known operation!")

    return sliced_data
