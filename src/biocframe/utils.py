from typing import Sequence, Union

from ._type_checks import is_list_of_type
from ._types import SlicerTypes

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def _match_to_indices(data: Sequence, indices: SlicerTypes) -> Union[slice, Sequence]:
    """Utility function to make slicer arguments more palatable.

    Args:
        data (Sequence): input data array to slice.
        indices (SlicerTypes): either a slice or
            a list of indices to keep.

    Returns:
        Union[slice, Sequence]: either a slice or list of indices.
    """

    if is_list_of_type(indices, str):
        diff = list(set(indices).difference(set(data)))
        if len(diff) > 0:
            raise ValueError(
                f"Cannot slice by value since {diff} do not exist in {data}"
            )

        return [i for i in range(len(indices)) if indices[i] in data]
    elif is_list_of_type(indices, bool):
        if len(indices) != len(data):
            raise ValueError(
                "Indices is a boolean vector, length should match the size of the data."
            )

        return [
            i for i in range(len(indices)) if (indices[i] is True or indices[i] == 1)
        ]
    elif isinstance(indices, slice) or is_list_of_type(indices, int):
        return indices

    raise TypeError("`indices` is not a supported type!")
