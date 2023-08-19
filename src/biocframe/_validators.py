from collections import OrderedDict
from typing import Any, MutableMapping, Optional, Sequence, Union

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def validate_rows(
    data: MutableMapping[str, Union[Sequence[Any], MutableMapping]],
    number_of_rows: Optional[int],
    row_names: Optional[Sequence[str]],
) -> int:
    """Validate rows of :py:class:`~biocframe.BiocFrame.BiocFrame` object.

    Args:
        data (MutableMapping[str, Union[Sequence[Any], MutableMapping]], optional):
            Dictionary of columns and their values. all columns must have the
            same length. Defaults to {}.
        number_of_rows (int, optional): Number of rows.
        row_names (Sequence[str], optional): Row index values.


    Raises:
        ValueError: when ``number_of_rows`` and ``data`` do not agree.

    Returns:
        int: Validated number of rows in ``data``.
    """
    incorrect_len_keys = []
    for k, v in data.items():
        tmpLen = len(v)

        if number_of_rows is None:
            number_of_rows = tmpLen
        elif number_of_rows != tmpLen:
            incorrect_len_keys.append(k)

    if len(incorrect_len_keys) > 0:
        raise ValueError(
            "`BiocFrame` expects all column in ``data`` to be equal"
            f"length, these columns: {incorrect_len_keys} do not."
        )

    if row_names is not None:
        if not validate_unique_list(row_names):
            raise ValueError("`row_names` must be unique!")

        if number_of_rows is None:
            number_of_rows = len(row_names)
        else:
            if len(row_names) != number_of_rows:
                raise ValueError(
                    "Length of `row_names` and `number_of_rows` do not match, "
                    f"l{len(row_names)} != {number_of_rows}"
                )

    return number_of_rows


def validate_cols(
    column_names: Sequence[str],
    data: MutableMapping[str, Union[Sequence[Any], MutableMapping]],
) -> Sequence[str]:
    """Validate columns of a :py:class:`biocframe.BiocFrame` object.

    Args:
        column_names (Sequence[str], optional): Column names, if not provided,
            its automatically inferred from data. Defaults to None.
        data (MutableMapping[str, Union[Sequence[Any], MutableMapping]], optional):
            a dictionary of columns and their values. all columns must have the
            same length. Defaults to {}.. Defaults to {}.

    Raises:
        ValueError: when `column_names` and `data` do not agree.
        TypeError: incorrect column type.

    Returns:
        Sequence[str]: list of columns names.
    """
    if column_names is None:
        column_names = list(data.keys())
    else:
        if len(column_names) != len(data.keys()):
            raise ValueError(
                "Number of columns mismatch between `column_names` and `data`"
            )

    # Technically should throw an error but
    # lets just fix it
    # column names and dict order should be the same
    incorrect_types = []
    new_odata = OrderedDict()
    for k in column_names:
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

    return column_names, data


def validate_unique_list(values: Sequence) -> bool:
    """Validate if a list has unique values.

    Args:
        values (Sequence): list of values to check.

    Returns:
        bool: True if all values are unique else False.
    """
    return len(set(values)) == len(values)
