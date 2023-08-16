from collections import OrderedDict
from typing import Any, MutableMapping, Optional, Sequence, Tuple, Union

import pandas as pd

from ._type_checks import is_list_of_type
from ._types import SlicerArgTypes, SlicerTypes
from ._validators import validate_cols, validate_rows, validate_unique_list
from .utils import match_to_indices

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


class BiocFrameIter:
    """An iterator to a `BiocFrame` object.

    Args:
        biocframe (BiocFrame): source object to iterate over.
    """

    def __init__(self, biocframe: "BiocFrame") -> None:
        self._bframe = biocframe
        self._current_index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._current_index < len(self._bframe):
            iter_row_index = (
                self._bframe.rowNames[self._current_index]
                if self._bframe.rowNames is not None
                else None
            )

            iter_slice = self._bframe.row(self._current_index)
            self._current_index += 1
            return (iter_row_index, iter_slice)

        raise StopIteration


class BiocFrame:
    """Initialize a `BiocFrame` object.

    `BiocFrame` is a lite implementation of :class:`pandas.DataFrame`.

    A key difference between these two classes is `BiocFrame` supports
    any :class:`collections.abc.Sequence`
    as a column. This allows us to be flexible, e.g: nested data frames
    or `BiocFrame` objects as columns.

    To create a `BiocFrame` object,

    .. code-block:: python

        obj = {
            "column1": [1, 2, 3],
            "nested": BiocFrame({"ncol1": [4, 5, 6]}),
            "column2": ["b", "n", "m"],
        }
        bframe = BiocFrame(obj)

    we expect each column provided to `BiocFrame` implements the `Sequence` interface,
    needs to implement length (`__len__`) and slice (`__getitem__`) methods.

    you can continue to access many properties through the getters and setters.
    e.g. `rowNames`, `colNames`, `dims`, `shape` etc.

    or slice the object

    .. code-block:: python

        sliced_bframe = bframe[3:7, 2:5]

    Args:
        data (MutableMapping[str, Union[Sequence[Any], MutableMapping]], optional):
            a dictionary of columns and their values. all columns must have the
            same length. Defaults to None.
        numberOfRows (int, optional): Number of rows. Defaults to None.
        rowNames (Sequence[str], optional): Row index values. Defaults to None.
        columnNames (Sequence[str], optional): column names, if not provided,
            is automatically inferred from data. Defaults to None.
        metadata (MutableMapping, optional): metadata. Defaults to None.

    Raises:
        ValueError: if rows or columns mismatch from data.

    """

    def __init__(
        self,
        data: Optional[
            MutableMapping[str, Union[Sequence[Any], MutableMapping]]
        ] = None,
        numberOfRows: Optional[int] = None,
        rowNames: Optional[Sequence[str]] = None,
        columnNames: Optional[Sequence[str]] = None,
        metadata: Optional[MutableMapping] = None,
    ) -> None:
        self._numberOfRows = numberOfRows
        self._rowNames = rowNames
        self._data = {} if data is None else data
        self._columnNames = columnNames
        self._metadata = metadata

        self._validate()

    def _validate(self):
        """Internal method to validate the object.

        Raises:
            ValueError: when provided object does not contain the
                same number of columns.
            ValueError: when row index is not unique.
        """

        self._numberOfRows = validate_rows(
            self._numberOfRows, self._rowNames, self._data
        )
        self._columnNames, self._data = validate_cols(self._columnNames, self._data)

        self._numberOfColumns = len(self._columnNames)

        if self._numberOfRows is None:
            self._numberOfRows = 0

    def __str__(self) -> str:
        pattern = (
            f"Class BiocFrame with {self.dims[0]} X {self.dims[1]} (rows, columns)\n"
            f"  column names: {self.columnNames if self._numberOfColumns > 1 else None}\n"
            f"  contains row index?: {self.rowNames is not None}"
        )
        return pattern

    @property
    def dims(self) -> Tuple[int, int]:
        """Dimensions of the BiocFrame.

        Returns:
            Tuple[int, int]: A tuple of number of rows and number of columns.
        """
        return (self._numberOfRows, self._numberOfColumns)

    @property
    def shape(self) -> Tuple[int, int]:
        """Dimensions of the BiocFrame.

        Returns:
            Tuple[int, int]: A tuple of number of rows and number of columns.
        """
        return self.dims

    @property
    def rowNames(self) -> Optional[Sequence[str]]:
        """Access row index (names).

        Returns:
            (Sequence[str], optional): row index names if available, else None.
        """
        return self._rowNames

    @rowNames.setter
    def rowNames(self, names: Optional[Sequence[str]]):
        """Set new row index.

        Args:
            names (Sequence[str], optional): new row names to set as index.

        Raises:
            ValueError: not the same as number of rows.
            ValueError: names is not unique.
        """

        if names is not None:
            if len(names) != self._numberOfRows:
                raise ValueError(
                    "Incorrect length of `names`, need to be "
                    f"{self._numberOfRows} but provided {len(names)}"
                )

            if not (validate_unique_list(names)):
                raise ValueError("row index must be unique!")

        self._rowNames = names

    @property
    def data(self) -> MutableMapping[str, Union[Sequence[Any], MutableMapping]]:
        """Access data (as dictionary).

        Returns:
            MutableMapping[str, Union[Sequence[Any], MutableMapping]]:
                dictionary of columns and their values.
        """
        return self._data

    @property
    def columnNames(self) -> Sequence[str]:
        """Access column names.

        Returns:
            Sequence[str]: list of column names.
        """
        return self._columnNames

    @columnNames.setter
    def columnNames(self, names: Sequence[str]):
        """Set new column names.

        Args:
            names (Sequence[str]): new column names.

        Raises:
            ValueError: if provided names not the same as number of columns.
        """

        if names is None:
            raise ValueError("column names cannot be `None`!")

        if len(names) != self._numberOfColumns:
            raise ValueError(
                "Incorrect length of `names`, need to be "
                f"{self._numberOfColumns} but provided {len(names)}"
            )

        if not (validate_unique_list(names)):
            raise ValueError("column names must be unique!")

        new_data = OrderedDict()
        for idx in range(len(names)):
            new_data[names[idx]] = self._data[self.columnNames[idx]]

        self._columnNames = names
        self._data = new_data

    @property
    def metadata(self) -> Optional[MutableMapping]:
        """Access metadata.

        Returns:
            (MutableMapping, optional): metadata object if available,
                usually a dictionary.
        """
        return self._metadata

    @metadata.setter
    def metadata(self, metadata: MutableMapping):
        """Set new metadata.

        Args:
            metadata (MutableMapping): new metadata object.
        """
        self._metadata = metadata

    def hasColumn(self, name: str) -> bool:
        """check if a column exists.

        Args:
            name (str): column name.

        Returns:
            bool: Whether the column exists in the BiocFrame.
        """
        return name in self.columnNames

    def has_column(self, name: str) -> bool:
        """check if a column exists.

        Args:
            name (str): column name.

        Returns:
            bool: Whether the column exists in the BiocFrame.
        """
        return self.hasColumn(name)

    def column(
        self, indexOrName: Union[str, int]
    ) -> Union[Sequence[Any], MutableMapping]:
        """Access a column by index or name.

        Args:
            indexOrName (Union[str, int]): index or name of the column.

        Raises:
            ValueError: if name is not in column names.
            ValueError: if index greater than number of columns.
            TypeError: if indexOrName is neither a string nor integer.

        Returns:
            Union[Sequence[Any], MutableMapping]: column from the object.
        """
        if isinstance(indexOrName, str):
            if indexOrName not in self.columnNames:
                raise ValueError(
                    f"{indexOrName} not in `BiocFrame` column names {self.columnNames}"
                )
            return self._data[indexOrName]
        elif isinstance(indexOrName, int):
            if indexOrName > self._numberOfColumns:
                raise ValueError(
                    f"{indexOrName} must be less than number of "
                    f"columns {self._numberOfColumns}"
                )
            return self._data[self.columnNames[indexOrName]]
        else:
            raise TypeError(
                "Unknown Type for `indexOrName`, must be either string or index"
            )

    def row(self, indexOrName: Union[str, int]) -> MutableMapping[str, Any]:
        """Access a row by index or name.

        Args:
            indexOrName (Union[str, int]): index or name of the row.

        Raises:
            ValueError: if name not in row names.
            ValueError: if index greater than number of rows.
            TypeError: if indexOrName is neither a string nor integer.

        Returns:
            Mapping[str, Any]: row from object
        """

        rindex = None
        if isinstance(indexOrName, str):
            if self.rowNames is not None:
                if indexOrName not in self.rowNames:
                    raise ValueError(f"{indexOrName} not in row index {self.rowNames}")

                rindex = self.rowNames.index(indexOrName)
            else:
                raise ValueError("cannot access by string, row index does not exist.")
        elif isinstance(indexOrName, int):
            if indexOrName > self._numberOfRows:
                raise ValueError(
                    f"{indexOrName} greater than number of rows {self._numberOfRows}"
                )
            rindex = indexOrName
        else:
            raise TypeError(
                "Unknown Type for `indexOrName`, must be either string or index"
            )

        if rindex is None:
            raise Exception(
                "It should've already failed. contact the authors "
                "with a minimum reproducible example"
            )

        row = OrderedDict()
        for k in self.columnNames:
            row[k] = self._data[k][rindex]

        return row

    def _slice(
        self,
        rowIndicesOrNames: Optional[SlicerTypes] = None,
        colIndicesOrNames: Optional[SlicerTypes] = None,
    ) -> "BiocFrame":
        """Internal method to slice by index or values.

        Args:
            rowIndicesOrVals (SlicerTypes, optional):
                row indices or names to keep. Defaults to None.
            colIndicesOrVals (SlicerTypes, optional):
                column indices or names to keep. Defaults to None.

        Returns:
            BiocFrame: sliced `BiocFrame` object.
        """

        new_data = OrderedDict()
        new_rowNames = self.rowNames
        new_columnNames = self.columnNames

        # slice the columns and data
        if colIndicesOrNames is not None:
            new_column_indices = match_to_indices(self.columnNames, colIndicesOrNames)

            if isinstance(new_column_indices, slice):
                new_columnNames = new_columnNames[new_column_indices]
            elif isinstance(new_column_indices, Sequence):
                new_columnNames = [new_columnNames[i] for i in new_column_indices]
            else:
                raise TypeError("column slice: unknown column indices type!")

        for col in new_columnNames:
            new_data[col] = self._data[col]

        # slice the rows of the data
        new_numberOfRows = None
        if rowIndicesOrNames is not None:
            new_row_indices = rowIndicesOrNames

            if self.rowNames is not None:
                new_row_indices = match_to_indices(self.rowNames, rowIndicesOrNames)

                if isinstance(new_row_indices, slice):
                    new_rowNames = new_rowNames[new_row_indices]
                elif isinstance(new_row_indices, Sequence):
                    new_rowNames = [new_rowNames[i] for i in new_row_indices]
                else:
                    raise TypeError("row slice: unknown slice type.")

            if isinstance(new_row_indices, slice):
                new_numberOfRows = len(range(new_row_indices.stop)[new_row_indices])
            elif is_list_of_type(new_row_indices, bool):
                new_row_indices = [
                    i for i in range(len(new_row_indices)) if new_row_indices[i] is True
                ]
                new_numberOfRows = len(new_row_indices)
            elif isinstance(new_row_indices, Sequence):
                new_numberOfRows = len(new_row_indices)
            else:
                raise TypeError("Row slice: unknown slice type")

            if is_list_of_type(new_row_indices, bool):
                new_row_indices = [
                    i for i in range(len(new_row_indices)) if new_row_indices[i] is True
                ]

            # since row names are not set, the
            # only option here is to slice by index
            if isinstance(new_row_indices, slice):
                for k, v in new_data.items():
                    new_data[k] = v[new_row_indices]
            elif is_list_of_type(new_row_indices, int):
                for k, v in new_data.items():
                    print(k, v)
                    if hasattr(v, "shape") and len(v.shape) > 1:
                        new_data[k] = v[new_row_indices, :]
                    else:
                        new_data[k] = [v[idx] for idx in new_row_indices]

            else:
                raise TypeError("row slice: not all row slices are integers!")
        else:
            new_numberOfRows = self._numberOfRows

        if new_numberOfRows is None:
            raise Exception(
                "This should not happen. Please contact the developers with"
                "a reproducible example!"
            )

        return BiocFrame(
            data=new_data,
            numberOfRows=new_numberOfRows,
            rowNames=new_rowNames,
            columnNames=new_columnNames,
        )

    # TODO: implement in-place or views
    def __getitem__(
        self,
        args: SlicerArgTypes,
    ) -> "BiocFrame":
        """Subset by index names or indices.

        Note: slice always returns a new `BiocFrame` object. If you need to access
        specific rows or columns, use the `row` or `column` methods.

        Usage:
            Slices can provided as a list of indices or slices or row/column names.
            e.g.:
                biocframe = BiocFrame({...})
                biocframe[0:2, 0:2]
                biocframe[[0,2], 0:2]
                biocframe[<List of column names>]

        Args:
            args (SlicerArgTypes): indices to slice.
                - Sequence[str]: Slice by column names.
                - list of indices or a boolean vector: slice by indices along the row and column axes.

        Raises:
            ValueError: Too many slices provided.
            TypeError: if provided args are not an expected type (`str`, `int`, `tuple`, `list`).

        Returns:
            BiocFrame: new sliced `BiocFrame` object.
        """

        # not an array, single str, slice by column
        if isinstance(args, str):
            return self._slice(None, [args])

        if isinstance(args, int):
            return self._slice([args], None)

        # not an array, a slice
        if isinstance(args, slice):
            return self._slice(args, None)

        # only possibility for a list is column names
        if isinstance(args, list):
            # are all args string
            all_strs = all([isinstance(k, str) for k in args])
            if all_strs:
                return self._slice(None, args)
            else:
                raise ValueError("provided `args` is not a list of column names")

        # tuple
        if isinstance(args, tuple):
            if len(args) == 0:
                raise ValueError("Arguments must contain atleast one slice")

            if len(args) == 1:
                return self._slice(args[0], None)
            elif len(args) == 2:
                return self._slice(args[0], args[1])

            raise ValueError(f"`args` has too many dimensions: {len(args)}")

        raise TypeError(
            "`args` is not supported, must be a `str`, `int`, `tuple`, `list`"
        )

    # TODO: implement in-place or views
    def __setitem__(self, name: str, value: Sequence[Any]):
        """Add or re-assign a value to a column.

        Args:
            name (str): Column name.
            value (Sequence[Any]): New value to set.

        Raises:
            ValueError: If length of `value` does not match the length of the object.
        """
        if len(value) != self._numberOfRows:
            raise ValueError(
                f"new column:{name} has incorrect number of values."
                f"need to be {self._numberOfRows} but provided {len(value)}"
            )

        self._data[name] = value

        if name not in self.columnNames:
            self._columnNames.append(name)
            self._numberOfColumns += 1

    # TODO: implement in-place or view
    def __delitem__(self, name: str):
        """Remove column from `BiocFrame`.

        Args:
            name (str): Name of column to remove.

        Raises:
            ValueError: if column does not exist.
        """
        if name not in self.columnNames:
            raise ValueError(f"Column: {name} does not exist.")

        del self._data[name]
        self._columnNames.remove(name)
        self._numberOfColumns -= 1

    def __len__(self) -> int:
        """Number of rows.

        Returns:
            int: number of rows.
        """
        return self._numberOfRows

    def __iter__(self) -> "BiocFrameIter":
        """Iterator over rows"""
        return BiocFrameIter(self)

    def toPandas(self) -> pd.DataFrame:
        """**Alias to `to_pandas`.**
        Convert `BiocFrame` to a `pandas.DataFrame` object.

        Returns:
            pd.DataFrame: a pandas DataFrame object.
        """
        return pd.DataFrame(
            data=self._data, index=self._rowNames, columns=self._columnNames
        )

    def to_pandas(self) -> pd.DataFrame:
        """Convert `BiocFrame` to a `pandas.DataFrame` object.

        Returns:
            pd.DataFrame: a pandas DataFrame object.
        """
        return pd.DataFrame(
            data=self._data, index=self._rowNames, columns=self._columnNames
        )

    # TODO: very primitive implementation, needs very robust testing
    # TODO: implement in-place, view
    def __array_ufunc__(self, func, method, *inputs, **kwargs) -> "BiocFrame":
        """Interface with NumPy array methods.


        Usage:
            np.sqrt(biocframe)

        Raises:
            TypeError: Input not a `BiocFrame` object

        Returns:
            BiocFrame: BiocFrame after the function is applied
        """

        input = inputs[0]
        if not isinstance(input, BiocFrame):
            raise TypeError("input not supported")

        for col in self.columnNames:
            if pd.api.types.is_numeric_dtype(pd.Series(input.column(col))):
                new_col = getattr(func, method)(input.column(col), **kwargs)
                input[col] = new_col

        return input

    # compatibility with Pandas
    @property
    def columns(self) -> Sequence[str]:
        """**Alias to column names.**

        Returns:
            Sequence[str]: list of column names.
        """
        return self.columnNames

    @property
    def index(self) -> Optional[Sequence[str]]:
        """**Alias to rowNames.**

        Returns:
            (Sequence[str], optional): list of row index names.
        """
        return self.rowNames

    # compatibility with R interfaces
    @property
    def rownames(self) -> Optional[Sequence[str]]:
        """**Alias to rowNames.**

        Returns:
            (Sequence[str], optional): list of row index names.
        """
        return self.rowNames

    @rownames.setter
    def rownames(self, names: Sequence[str]):
        """**Alias to rowNames.**

        Args:
            names (Sequence[str]): new row index.
        """
        self.rowNames = names

    @property
    def colnames(self) -> Sequence[str]:
        """Access column names.

        Returns:
            Sequence[str]: list of column names.
        """
        return self.columnNames

    @colnames.setter
    def colnames(self, names: Sequence[str]):
        """**Alias to colNames.**

        Args:
            names (Sequence[str]): new column names.
        """
        self.colNames = names
