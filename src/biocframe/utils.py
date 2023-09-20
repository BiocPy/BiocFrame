"""Utility functions for biocframe."""

from typing import Any, List, Sequence, Tuple, Union, cast, overload
from warnings import warn

from ._type_checks import is_list_of_type
from .types import (
    AllSlice,
    AtomicSlice,
    ColSlice,
    RowSlice,
    SeqSlice,
    SimpleSlice,
    TupleSlice,
)

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


@overload
def match_to_indices(data: List[Any], query: slice) -> Tuple[slice, bool]:
    ...


@overload
def match_to_indices(
    data: List[Any],
    query: Union[SeqSlice, TupleSlice, AtomicSlice, RowSlice, ColSlice],
) -> Tuple[Sequence[int], bool]:
    ...


def match_to_indices(
    data: List[Any], query: AllSlice
) -> Tuple[SimpleSlice, bool]:
    """Utility function to make slicer arguments more palatable.

    Args:
        data (List): Input data array to slice.
        query (SlicerTypes): Either a slice or a list of int indices to keep.

    Returns:
        SlicerTypes:
            Resolved list of indices.
        bool:
            `True` if its a unary slice.
    """
    resolved_indices = None
    is_unary = False

    if isinstance(query, str):
        resolved_indices = [data.index(query)]
        is_unary = True
    elif isinstance(query, int):
        if abs(query) > len(data):
            raise ValueError("Integer index is greater than the shape.")
        resolved_indices = [query]
        is_unary = True
    elif isinstance(query, slice):
        # resolved_indices = list(range(len(data))[query])
        resolved_indices = query
    else:
        if is_list_of_type(query, bool):
            if len(query) != len(data):
                warn(
                    "`indices` is a boolean vector, length should match the size of the data."
                )

            resolved_indices = [
                i for i in range(len(query)) if query[i] is True
            ]
        elif is_list_of_type(query, int):
            resolved_indices = cast(List[int], query)
        elif is_list_of_type(query, str):
            diff = list(set(query).difference(set(data)))
            if len(diff) > 0:
                raise ValueError(
                    "`indices` is a string vector, not all values are present in data."
                )

            resolved_indices = [data.index(i) for i in query]
        else:
            raise TypeError("`indices` is a list of unsupported types!")

    return resolved_indices, is_unary


def slice_or_index(data: Any, query: SimpleSlice) -> List[Any]:
    """Utility function to slice or index data.

    Args:
        data (Any): Input data array to slice.
        query (BasicSlice): Either a `slice` or a list of int indices to keep.

    Returns:
        List[Any]: The sliced data.

    Raises:
        TypeError: If the query is not a slice or a list.
    """
    sliced_data: List[Any]
    if isinstance(query, slice):
        sliced_data = data[query]
    else:
        if not isinstance(data, list):
            try:
                return data[query]
            except Exception:
                pass

        sliced_data = [data[i] for i in query]

    return sliced_data
