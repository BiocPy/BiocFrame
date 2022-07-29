from typing import Any, Dict, List, Union


__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def extract_keys(
    obj: Dict[str, Union[List[Any], Dict]], prefix: str = None
) -> List[str]:
    """Recursively extract keys from a dictionary object

    Args:
        obj (Dict[str, Union[List, Dict]]): the dictionary object of columns
        prefix (str, optional): Prefix to append to names. Defaults to None.

    Returns:
        List[str]: all keys (including nested) keys from the objected
    """

    keys = []
    dims = []
    for k, v in obj.items():
        if isinstance(v, dict):
            kn, dn = extract_keys(
                v, prefix=f"{prefix}.{k}" if prefix is not None else f"{k}"
            )
            keys.extend(kn)
            dims.extend(dn)
        else:
            keys.append(f"{prefix}.{k}" if prefix is not None else f"{k}")
            dims.append(len(v))

    return (keys, dims)


def slice_data(
    obj: Dict[str, Union[List[Any], Dict]], rowIndices: Union[List[int], slice]
) -> Dict[str, Union[List[Any], Dict]]:
    """Recursively slice a data object

    Args:
        obj (Dict[str, Union[List, Dict]]): columnar represented data to slice
        rowIndices (Union[List[int], slice]): rows to keep

    Returns:
         Dict[str, Union[List[Any], Dict]]: sliced object
    """

    slices = {}
    for k, v in obj.items():
        if isinstance(v, dict):
            slices[k] = slice_data(v, rowIndices=rowIndices)
        else:
            slices[k] = _slice(v, rowIndices)

    return slices


def _slice(data: List[Any], rows: Union[List[int], slice]) -> List[Any]:
    """slice an array

    Args:
        data (List[Any]): input data array to slice
        rows (Union[List[int], slice): either a slice or a list of indices to keep

    Returns:
        List[Any]: sliced data array
    """

    if isinstance(rows, list):
        return [data[i] for i in rows]
    elif isinstance(rows, slice):
        return data[rows]
