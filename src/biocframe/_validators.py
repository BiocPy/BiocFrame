from collections import OrderedDict
from typing import Any, MutableMapping, Sequence, Union

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def validate_rows(
    numberOfRows: int,
    rowNames: Sequence[str],
    data: MutableMapping[str, Union[Sequence[Any], MutableMapping]],
) -> int:
    """Validate rows of `BiocFrame` object.

    Args:
        numberOfRows (int, optional): Number of rows. Defaults to None.
        rowNames (Sequence[str], optional): Row index values . Defaults to None.
        data (MutableMapping[str, Union[Sequence[Any], MutableMapping]], optional):
            a dictionary of columns and their values. all columns must have the
            same length. Defaults to {}.

    Raises:
        ValueError: when `numberOfRows` and `data` do not agree.

    Returns:
        int: validated number of rows in data.
    """
    incorrect_len_keys = []
    for k, v in data.items():
        tmpLen = len(v)

        if numberOfRows is None:
            numberOfRows = tmpLen
        elif numberOfRows != tmpLen:
            incorrect_len_keys.append(k)

    if len(incorrect_len_keys) > 0:
        raise ValueError(
            "Expected all objects in `data` to be equal"
            f"length, these columns: {incorrect_len_keys} do not"
        )

    if rowNames is not None:
        if not validate_unique_list(rowNames):
            raise ValueError("rowNames must be unique!")

        if numberOfRows is None:
            numberOfRows = len(rowNames)
        else:
            if len(rowNames) != numberOfRows:
                raise ValueError("length of `rowNames` and `numberOfRows` do not match")

    return numberOfRows


def validate_cols(
    columnNames: Sequence[str],
    data: MutableMapping[str, Union[Sequence[Any], MutableMapping]],
) -> Sequence[str]:
    """Validate columns of a `BiocFrame` object.

    Args:
        columnNames (Sequence[str], optional): column names, if not provided,
            its automatically inferred from data. Defaults to None.
        data (MutableMapping[str, Union[Sequence[Any], MutableMapping]], optional):
            a dictionary of columns and their values. all columns must have the
            same length. Defaults to {}.. Defaults to {}.

    Raises:
        ValueError: when `columnNames` and `data` do not agree.
        TypeError: incorrect column type.

    Returns:
        Sequence[str]: list of columns names.
    """
    if columnNames is None:
        columnNames = list(data.keys())
    else:
        if len(columnNames) != len(data.keys()):
            raise ValueError(
                "Number of columns mismatch between `columnNames` and `data`"
            )

    # Technically should throw an error but
    # lets just fix it
    # column names and dict order should be the same
    incorrect_types = []
    new_odata = OrderedDict()
    for k in columnNames:
        # check for types
        col_value = data[k]

        if not (hasattr(col_value, "__len__") and hasattr(col_value, "__getitem__")):
            incorrect_types.append(k)

        new_odata[k] = data[k]

    if len(incorrect_types) > 0:
        raise TypeError(
            "All columns in data must support `len` and "
            f"`slice` operations. columns: {incorrect_types} "
            f"do not support these methods."
        )

    data = new_odata

    return columnNames, data


def validate_unique_list(values: Sequence) -> bool:
    """Validate if a list has unique values.

    Args:
        values (Sequence): list of values to check.

    Returns:
        bool: True if all values are unique else False.
    """
    return len(set(values)) == len(values)
