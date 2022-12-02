from typing import Any, List, Union, Sequence


__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def match_to_indices(
    data: Sequence[Any], indices: Union[List[int], slice, List[str]]
) -> Union[slice, Sequence[Any]]:
    """slice an array

    Args:
        data (Sequence[Any]): input data array to slice
        indices (Union[List[int], slice, List[str]): either a slice or a list of indices to keep

    Returns:
        Union[slice, Sequence[Any]]: either a slice or list of indices
    """

    if isinstance(indices, slice):
        return indices
    elif isinstance(indices, list):
        all_strs = all([isinstance(k, str) for k in indices])
        # slice by value
        if all_strs:
            diff = list(set(indices).difference(set(data)))
            if len(diff) > 0:
                raise ValueError(
                    f"Cannot slice by value since {diff} do not exist in {data}"
                )

            return [i for i in range(len(indices)) if indices[i] in data]
        else:
            return indices

    raise TypeError(f"`indices` is neither a `list` nor a `slice`")
