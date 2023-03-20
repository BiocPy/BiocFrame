from typing import Any, List, Union, Sequence, Optional, Tuple, MutableMapping
from .utils import match_to_indices

from ._validators import validate_rows, validate_cols, validate_unique_list
from collections import OrderedDict
import pandas as pd

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


class BiocFrame:
    def __init__(
        self,
        data: Optional[MutableMapping[str, Union[List[Any], MutableMapping]]] = None,
        numberOfRows: Optional[int] = None,
        rowNames: Optional[Sequence[str]] = None,
        columnNames: Optional[Sequence[str]] = None,
        metadata: Optional[MutableMapping] = None,
    ) -> None:
        """Initialize a BiocFrame object.

        `BiocFrame` supports many methods similar to a pandas `DataFrame`. 
        A key difference between these two classes is `BiocFrame` supports 
        any `Sequence` type 
        (https://docs.python.org/3/library/stdtypes.html#sequence-types-list-tuple-range) 
        as a column. This allows us to be flexible, e.g: nested data frames 
        or `BiocFrame` objects as columns.

        Raises:
            ValueError: if rows or columns mismatch from data.

        Args:
            data (MutableMapping[str, Union[List[Any], MutableMapping]], optional): 
                a dictionary of colums and their values. all columns must have the 
                same length. Defaults to None.
            numberOfRows (int, optional): Number of rows. Defaults to None.
            rowNames (Sequence[str], optional): Row index values . Defaults to None.
            columnNames (Sequence[str], optional): column names, if not provided, 
                its automatically inferred from data. Defaults to None.
            metadata (MutableMapping, optional): metadata. Defaults to None.
        """
        self._numberOfRows = numberOfRows
        self._rowNames = rowNames
        self._data = {} if data is None else data
        self._columnNames = columnNames
        self._metadata = metadata

        self._validate()

        self._iterIdx = 0

    def _validate(self):
        """Internal method to validate the object.

        Raises:
            ValueError: when provided object does not contain columns of same length.
        """

        self._numberOfRows = validate_rows(
            self._numberOfRows, self._rowNames, self._data
        )
        self._columnNames = validate_cols(self._columnNames, self._data)

        self._numberOfColumns = len(self._columnNames)

        if self._numberOfRows is None:
            self._numberOfRows = 0

    def __str__(self) -> str:
        pattern = (
            f"Class BiocFrame with {self.dims[0]} rows and {self.dims[1]} columns\n"
            f"  columnNames: {self.columnNames}\n"
            f"  contains rowNames?: {self.rowNames is None}"
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
            Optional[Sequence[str]]: row index names if available else None.
        """
        return self._rowNames

    @property
    def data(self) -> MutableMapping[str, Union[List[Any], MutableMapping]]:
        """Access data (as dictionary).

        Returns:
            MutableMapping[str, Union[List[Any], MutableMapping]]: 
                dictionary of columns and their values.
        """
        return self._data

    @rowNames.setter
    def rowNames(self, names: Optional[Sequence[str]]):
        """Set new index.

        Args:
            names (Sequence[str], optional): new row names to set as index.

        Raises:
            ValueError: if length of new index not the same as number of rows.
        """

        if names is not None:
            if len(names) != self._numberOfRows:
                raise ValueError(
                    "Incorrect length of `names`, need to be "
                    f"{self._numberOfRows} but provided {len(names)}"
                )

            if not (validate_unique_list(names)):
                raise ValueError("names must be unique!")

        self._rowNames = names

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
            raise ValueError("Column names cannot be None!")

        if len(names) != self._numberOfColumns:
            raise ValueError(
                "Incorrect length of `names`, need to be "
                f"{self._numberOfColumns} but provided {len(names)}"
            )

        new_data = OrderedDict()
        for idx in range(len(names)):
            new_data[names[idx]] = self._data[self._columnNames[idx]]

        self._columnNames = names
        self._data = new_data

    @property
    def metadata(self) -> Optional[MutableMapping]:
        """Access metadata.

        Returns:
            Optional[MutableMapping]: metadata object if available, 
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
        return name in self._columnNames

    def column(
        self, indexOrName: Union[str, int]
    ) -> Union[Sequence[Any], MutableMapping]:
        """Access a column by index or name.

        Args:
            indexOrName (Union[str, int]): index or name of the column.

        Raises:
            ValueError: if name is not in column names.
            ValueError: if index greather than number of columns.
            TypeError: if indexOrName is neither a string nor integer.

        Returns:
            Union[Sequence[Any], MutableMapping]: column from the object.
        """
        if isinstance(indexOrName, str):
            if indexOrName not in self._columnNames:
                raise ValueError(
                    f"{indexOrName} not in BiocFrame column names {self._columnNames}"
                )
            return self._data[indexOrName]
        elif isinstance(indexOrName, int):
            if indexOrName > self._numberOfColumns:
                raise ValueError(
                    f"{indexOrName} must be less than number of "
                    f"columns {self._numberOfColumns}"
                )
            return self._data[self._columnNames[indexOrName]]
        else:
            raise TypeError(
                "Unkown Type for `indexOrName`, must be either string or index"
            )

    def row(self, indexOrName: Union[str, int]) -> MutableMapping[str, Any]:
        """Access a row by index or name.

        Args:
            indexOrName (Union[str, int]): index or name of the row.

        Raises:
            ValueError: if name not in row names.
            ValueError: if index greather than number of rows.
            TypeError: if indexOrName is neither a string nor integer.

        Returns:
            Mapping[str, Any]: row from object
        """

        rindex = None
        if isinstance(indexOrName, str):
            if indexOrName not in self._rowNames:
                raise ValueError(
                    f"{indexOrName} not in BiocFrame column names {self._rowNames}"
                )

            rindex = self._rowNames.index(indexOrName)
        elif isinstance(indexOrName, int):
            if indexOrName > self._numberOfRows:
                raise ValueError(
                    f"{indexOrName} greater than number of columns {self._numberOfRows}"
                )
            rindex = indexOrName
        else:
            raise TypeError(
                "Unkown Type for `indexOrName`, must be either string or index"
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
        rowIndicesOrNames: Optional[Union[Sequence[int], Sequence[str], slice]] = None,
        colIndicesOrNames: Optional[Union[Sequence[int], Sequence[str], slice]] = None,
    ) -> "BiocFrame":
        """Internal method to slice by index or values.

        Args:
            rowIndicesOrVals (Union[Sequence[int], Sequence[str], slice], optional): 
                row indices or vals to keep. Defaults to None.
            colIndicesOrVals (Union[Sequence[int], Sequence[str], slice], optional): 
                column indices or vals to keep. Defaults to None.

        Returns:
            BiocFrame: sliced `BiocFrame` object.
        """

        new_data = OrderedDict()
        new_rowNames = self._rowNames
        new_columnNames = self._columnNames

        # slice the columns and data
        if colIndicesOrNames is not None:
            new_column_indices = match_to_indices(self._columnNames, colIndicesOrNames)

            if isinstance(new_column_indices, slice):
                new_columnNames = new_columnNames[new_column_indices]
            elif isinstance(new_column_indices, list):
                new_columnNames = [new_columnNames[i] for i in new_column_indices]
            else:
                raise TypeError("Column Slice: Unknown match_to_indices type")

        for col in new_columnNames:
            new_data[col] = self._data[col]

        # slice the rows of the data
        if rowIndicesOrNames is not None:
            new_row_indices = rowIndicesOrNames
            if self._rowNames is not None:
                new_row_indices = match_to_indices(self._rowNames, rowIndicesOrNames)

                if isinstance(new_row_indices, slice):
                    new_rowNames = new_rowNames[new_row_indices]
                elif isinstance(new_row_indices, list):
                    new_rowNames = [new_rowNames[i] for i in new_row_indices]
                else:
                    raise TypeError("Row Slice: Unknown match_to_indices type")

            # since row names are not set, the
            # only option here is to slice by index
            if isinstance(new_row_indices, slice):
                for k, v in new_data.items():
                    new_data[k] = v[new_row_indices]
            elif all([isinstance(k, int) for k in new_row_indices]):
                for k, v in new_data.items():
                    new_data[k] = [v[idx] for idx in new_row_indices]
            else:
                raise TypeError("Row Slice: not all row slices are integers")

        return BiocFrame(
            data=new_data, rowNames=new_rowNames, columnNames=new_columnNames
        )

    # TODO: implement inplace, view
    def __getitem__(
        self,
        args: Union[
            Sequence[str],
            Tuple[Union[Sequence[int], slice], Optional[Union[Sequence[int], slice]]],
        ],
    ) -> "BiocFrame":
        """Subset by index or indices.

        Note: Slice always returns another BiocFrame object. If you need to access
        specific rows or columns, use the `row` or `column` methods.

        Usage:
            Slices can provided as a list of indices or slices or row/column names.
            e.g.:
                bframe = BiocFrame({...}) 
                bframe[0:2, 0:2]
                bframe[[0,2], 0:2]
                bframe[<List of column names>]

        Args:
            args (Union[Sequence[str], Tuple[Union[Sequence[int], slice], Optional[Union[Sequence[int], slice]]]]): indices to slice.
                - Sequence[str]: Slice by column names.
                - Tuple[Union[Sequence[int], slice], Optional[Union[Sequence[int], slice]]]: slice by indices along the row and column axes.

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
            if len(args) == 1:
                return self._slice(args[0], None)
            elif len(args) == 2:
                return self._slice(args[0], args[1])

            raise ValueError(f"`args` has too many dimensions: {len(args)}")

        raise TypeError(
            "`args` is not supported, must to a `str`, `int`, `tuple`, `list`"
        )

    # TODO: implement inplace, view
    def __setitem__(self, key: str, newvalue: Sequence[Any]):
        """Set/Assign a value to a column.

        Args:
            key (str): Column name.
            newvalue (List[Any]): New value to set.

        Raises:
            ValueError: If length of `newvalue` does not match the length of the object.
        """
        if len(newvalue) != self._numberOfRows:
            raise ValueError(
                f"new column:{key} has incorrect number of values. need to be {self._numberOfRows} but provided {len(newvalue)}"
            )

        self._data[key] = newvalue

        if key not in self._columnNames:
            self._columnNames.append(key)
            self._numberOfColumns += 1

    # TODO: implement inplace, view
    def __delitem__(self, name: str):
        """Remove column from `BiocFrame`.

        Args:
            name (str): Name of column to remove.

        Raises:
            ValueError: if column does not exist.
        """
        if name not in self._columnNames:
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

    def __iter__(self) -> "BiocFrame":
        """Iterator over rows"""
        return self

    def __next__(self) -> Tuple[Union[int, str], MutableMapping]:
        """Get next value from Iterator.

        Raises:
            StopIteration: when Index is out of range.
        """
        try:
            index_row = self._iterIdx
            if self._rowNames is not None:
                index_row = self._rowNames[self._iterIdx]

            iter_slice = self.row(self._iterIdx)
        except IndexError:
            self._iterIdx = 0
            raise StopIteration

        self._iterIdx += 1
        return (index_row, iter_slice)

    def toPandas(self) -> pd.DataFrame:
        """Convert `BiocFrame` to a `Pandas.DataFrame` object.

        Returns:
            pd.DataFrame: a Pandas Dataframe object.
        """
        return pd.DataFrame(
            data=self._data, index=self._rowNames, columns=self._columnNames
        )

    # TODO: very primilimary implementation, probably a lot more to do here
    # TODO: implement inplace, view
    def __array_ufunc__(self, func, method, *inputs, **kwargs) -> "BiocFrame":
        """Interface with numpy array methods

        Usage:
            np.sqrt(bframe)

        Raises:
            TypeError: Input not a `BiocFrame` object

        Returns:
            BiocFrame: BiocFrame after the function is applied
        """

        input = inputs[0]
        if not isinstance(input, BiocFrame):
            raise TypeError("input not supported")

        for col in self._columnNames:
            if pd.api.types.is_numeric_dtype(pd.Series(input.column(col))):
                new_col = getattr(func, method)(input.column(col), **kwargs)
                input[col] = new_col

        return input

    # compatibility with Pandas
    @property
    def columns(self) -> Sequence[str]:
        """Access column names.

        Returns:
            Sequence[str]: list of column names.
        """
        return self._columnNames

    # compatibility with R interfaces
    @property
    def rownames(self) -> Sequence[str]:
        """Access row index.

        Returns:
            Sequence[str]: list of row index names.
        """
        return self.rowNames

    @property
    def colnames(self) -> Sequence[str]:
        """Access column names.

        Returns:
            Sequence[str]: list of column names.
        """
        return self.columnNames
