from typing import Any, List, Union, Sequence


__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


# def iterative_extract_keys(
#     obj: Dict[str, Union[Sequence[Any], Mapping]], prefix: str = None
# ) -> List[str]:
#     """Recursively extract keys from a dictionary object

#     Args:
#         obj (Dict[str, Union[List, Dict]]): the dictionary object of columns
#         prefix (str, optional): Prefix to append to names. Defaults to None.

#     Returns:
#         List[str]: all keys (including nested) keys from the objected
#     """

#     keys = []
#     dims = []
#     for k, v in obj.items():
#         if isinstance(v, dict):
#             kn, dn = iterative_extract_keys(
#                 v, prefix=f"{prefix}.{k}" if prefix is not None else f"{k}"
#             )
#             keys.extend(kn)
#             dims.extend(dn)
#         else:
#             keys.append(f"{prefix}.{k}" if prefix is not None else f"{k}")
#             dims.append(len(v))

#     return (keys, dims)


# def iterative_slice_data(
#     obj: Dict[str, Union[Sequence[Any], Mapping]],
#     rowIndices: Union[List[int], slice],
# ) -> Dict[str, Union[Sequence[Any], Mapping]]:
#     """Recursively slice a data object

#     Args:
#         obj (Dict[str, Union[List, Dict]]): columnar represented data to slice
#         rowIndices (Union[List[int], slice]): rows to keep

#     Returns:
#          Dict[str, Union[List[Any], Dict]]: sliced object
#     """

#     slices = {}
#     for k, v in obj.items():
#         if isinstance(v, dict):
#             slices[k] = iterative_slice_data(v, rowIndices=rowIndices)
#         else:
#             slices[k] = match_to_indices(v, rowIndices)

#     return slices


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
