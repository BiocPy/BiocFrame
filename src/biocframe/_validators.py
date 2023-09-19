"""Validators for :py:class:`~biocframe.BiocFrame.BiocFrame` object."""

from typing import Any, List, Optional, Tuple

from .types import DataType

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def validate_rows(
    data: DataType,
    number_of_rows: Optional[int] = None,
    row_names: Optional[List[str]] = None,
) -> int:
    """Validate rows of :py:class:`~biocframe.BiocFrame.BiocFrame` object.

    Args:
        data (MutableMapping[str, Union[List, MutableMapping]], optional):
            Dictionary of columns and their values. all columns must have the
            same length. Defaults to {}.
        number_of_rows (int, optional): Number of rows.
        row_names (List[str], optional): Row index values.


    Raises:
        ValueError: When ``number_of_rows`` does the match the length of
            columns in ``data``.

    Returns:
        int: Validated number of rows in ``data``.
    """
    lengths = {k: len(v) for k, v in data.items()}
    mean_len = sum(lengths.values()) / len(lengths.values())
    int_mean_len = int(mean_len)

    if int_mean_len != mean_len or (
        number_of_rows is not None and int_mean_len != number_of_rows
    ):
        number_of_rows = (
            int_mean_len if number_of_rows is None else number_of_rows
        )
        bad_rows = [k for k, v in lengths.items() if v != number_of_rows]
        raise ValueError(
            "`BiocFrame` expects all columns in ``data`` to be of equal"
            f"length, but these are not: {bad_rows}."
        )
    else:
        number_of_rows = int_mean_len

    if row_names is not None:
        if not validate_unique_list(row_names):
            raise ValueError("`row_names` must be unique!")

        if len(row_names) != number_of_rows:
            raise ValueError(
                "Length of `row_names` and `number_of_rows` do not match, "
                f"l{len(row_names)} != {number_of_rows}"
            )

    return number_of_rows


def validate_cols(
    column_names: Optional[List[str]] = None,
    data: DataType = {},
) -> Tuple[List[str], DataType]:
    """Validate columns of a :py:class:`biocframe.BiocFrame` object.

    Args:
        column_names (List[str], optional): Column names, if not provided,
            its automatically inferred from data. Defaults to None.
        data (MutableMapping[str, Union[List, MutableMapping]], optional):
            a dictionary of columns and their values. all columns must have the
            same length. Defaults to {}.

    Raises:
        ValueError: When ``column_names`` do not match the keys from ``data``.
        TypeError: Incorrect column type.

    Returns:
        List[str]: List of columns names.
    """
    if column_names is None:
        column_names = list(data.keys())
    else:
        if len(column_names) != len(data.keys()):
            raise ValueError(
                "Mismatch in number of columns between 'column_names' and "
                "'data`'."
            )

        if len(set(column_names).difference(data.keys())) > 0:
            raise ValueError(
                "Not all columns from `column_names` are present in `data`."
            )

        if len(set(data.keys()).difference(column_names)) > 0:
            raise ValueError(
                "Not all columns from `data` are present in `column_names`."
            )

    # Technically should throw an error but lets just fix it column names and
    # dict order should be the same
    incorrect_types: List[str] = [
        k
        for k, v in data.items()
        if not (hasattr(v, "__len__") and hasattr(v, "__getitem__"))
    ]

    if len(incorrect_types) > 0:
        raise TypeError(
            "`data` only accepts columns that supports `len` and "
            "`slice` operations. these columns do not support these methods: "
            f"{', '.join(incorrect_types)}."
        )

    return column_names, data


def validate_unique_list(values: List[Any]) -> bool:
    """Validate if ``values`` contains unique values.

    Args:
        values (List): List to check.

    Returns:
        bool: `True` if all values are unique else False.
    """
    return len(set(values)) == len(values)
