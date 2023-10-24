from typing import Any, Dict, List, Optional, Tuple
from warnings import warn

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def validate_rows(
    data: Dict[str, Any],
    number_of_rows: Optional[int],
    row_names: Optional[List[str]],
) -> int:
    """Validate rows of :py:class:`~biocframe.BiocFrame.BiocFrame` object.

    Args:
        data (Dict[str, Any], optional):
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
    incorrect_len_keys = []
    for k, v in data.items():
        tmpLen = len(v)

        if number_of_rows is None:
            number_of_rows = tmpLen
        elif number_of_rows != tmpLen:
            incorrect_len_keys.append(k)

    if len(incorrect_len_keys) > 0:
        raise ValueError(
            "All columns in ``data`` must be the same "
            f"length, these columns do not: {', '.join(incorrect_len_keys)}."
        )

    if row_names is not None:
        if not validate_unique_list(row_names):
            warn("`row_names` are not unique!")

        if number_of_rows is None:
            number_of_rows = len(row_names)
        else:
            if len(row_names) != number_of_rows:
                raise ValueError(
                    "Length of `row_names` and `number_of_rows` do not match, "
                    f"{len(row_names)} != {number_of_rows}"
                )

    return number_of_rows


def validate_cols(
    column_names: List[str],
    data: Dict[str, Any],
    mcols: Optional["BiocFrame"],
) -> Tuple[List[str], Dict[str, Any]]:
    """Validate columns of a :py:class:`biocframe.BiocFrame` object.

    Args:
        column_names (List[str], optional): Column names, if not provided,
            its automatically inferred from data. Defaults to None.
        data (Dict[str, Any], optional):
            a dictionary of columns and their values. all columns must have the
            same length. Defaults to {}. Defaults to {}.

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
                "Number of columns mismatch between `column_names` and `data`."
            )

        if len(set(column_names).difference(data.keys())) > 0:
            raise ValueError(
                "Not all columns from `column_names` are present in `data`."
            )

        if len(set(data.keys()).difference(column_names)) > 0:
            raise ValueError(
                "Not all columns from `data` are present in `column_names`."
            )

    # Technically should throw an error but
    # lets just fix it
    # column names and dict order should be the same
    incorrect_types = []
    for k in column_names:
        # check for types
        col_value = data[k]

        if not (hasattr(col_value, "__len__") and hasattr(col_value, "__getitem__")):
            incorrect_types.append(k)

    if len(incorrect_types) > 0:
        raise TypeError(
            "`data` only accepts columns that supports `len` and "
            "`slice` operations. these columns do not support these methods: "
            f"{', '.join(incorrect_types)}."
        )

    if mcols is not None:
        if mcols.shape[0] != len(column_names):
            raise ValueError("Number of rows in `mcols` should be equal to the number of columns.")
        if mcols.row_names is not None:
            if mcols.row_names != column_names:
                raise ValueError("Row names of `mcols` should be equal to the column names.")

    return column_names, data, mcols


def validate_unique_list(values: List) -> bool:
    """Check if ``values`` contains unique values.

    Args:
        values (List): List to check.

    Returns:
        bool: `True` if all values are unique else False.
    """
    return len(set(values)) == len(values)
