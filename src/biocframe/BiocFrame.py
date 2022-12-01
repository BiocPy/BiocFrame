from typing import Any, List, Union, Mapping, Sequence, Optional, Tuple
from .utils import match_to_indices
from collections import OrderedDict
import pandas as pd
import numpy as np

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


class BiocFrame:
    def __init__(
        self,
        data: Optional[Mapping[str, Union[List[Any], Mapping]]] = {},
        numberOfRows: Optional[int] = None,
        rowNames: Optional[Sequence[str]] = None,
        columnNames: Optional[Sequence[str]] = None,
        metadata: Optional[Mapping] = None,
    ) -> None:

        self._numberOfRows = numberOfRows
        self._rowNames = rowNames
        self._data = data
        self._columnNames = columnNames
        self._metadata = metadata

        self._validate()

    def _validate(self):
        """Internal method to validate the object

        Raises:
            ValueError: when provided object does not contain columns of same length
        """
        incorrect_len_keys = []
        for k, v in self._data.items():
            tmpLen = len(v)

            if self._numberOfRows is None:
                self._numberOfRows = tmpLen
            elif self._numberOfRows != tmpLen:
                incorrect_len_keys.append(k)

        if len(incorrect_len_keys) > 0:
            raise ValueError(
                f"Expected all objects in `data` to be equal length, these columns: {incorrect_len_keys} do not"
            )

        if self._columnNames is None:
            self._columnNames = list(self._data.keys())
        else:
            if len(self._columnNames) != len(self._data.keys()):
                raise ValueError(f"`columnNames` and `data` order do not match")

            # Technically should throw an error but
            # lets just fix it
            # colnames and dict order should be the same
            new_odata = OrderedDict()
            for k in self._columnNames:
                new_odata[k] = self._data[k]

            self._data = new_odata

        self._numberOfColumns = len(self._columnNames)

        if self._rowNames:
            if self._numberOfRows is None:
                self._numberOfRows = len(self._rowNames)
            else:
                if len(self._rowNames) != len(self._numberOfRows):
                    raise ValueError(f"`rowNames` and `numberOfRows` do not match")

        if self._numberOfRows == None:
            self._numberOfRows = 0

    def __str__(self) -> str:
        pattern = """
        Class BiocFrame with {} rows and {} columns
          columnNames: {}
          contains rowNames?: {}
        """
        return pattern.format(
            self.dims[0], self.dims[1], self.columnNames, self.rowNames is None
        )

    @property
    def dims(self) -> Tuple[int, int]:
        """Dimensions of the BiocFrame

        Returns:
            Tuple[int, int]: A tuple of number of rows and number of columns
        """
        return (self._numberOfRows, self._numberOfColumns)

    @property
    def rowNames(self) -> Sequence[str]:
        """Access row index of BiocFrame

        Returns:
            Sequence[str]: a list of row index names
        """
        return self._rowNames

    @rowNames.setter
    def rowNames(self, names: Sequence[str]):
        """Set new row index

        Args:
            names (Sequence[str]): new row index list

        Raises:
            Exception: length of new index not the same as number of rows
        """
        if len(names) != self._numberOfRows:
            raise Exception(
                f"Incorrect length of `names`, need to be {self._numberOfRows} but provided {len(names)}"
            )

        self._rowNames = names

    @property
    def columnNames(self) -> Sequence[str]:
        """Access column names of BiocFrame

        Returns:
            Sequence[str]: a list of column names
        """
        return self._columnNames

    @columnNames.setter
    def columnNames(self, names: Sequence[str]):
        """Set new column names

        Args:
            names (Sequence[str]): new column names list

        Raises:
            Exception: length of new index not the same as number of columns
        """
        if len(names) != self._numberOfColumns:
            raise Exception(
                f"Incorrect length of `names`, need to be {self._numberOfColumns} but provided {len(names)}"
            )

        new_data = OrderedDict()
        for idx in range(len(names)):
            new_data[names[idx]] = self._data[self._columnNames[idx]]

        self._columnNames = names
        self._data = new_data

    @property
    def metadata(self) -> Mapping:
        """Access metadata of the BiocFrame

        Returns:
            Mapping: metadata object, usually a dictionary
        """
        return self._metadata

    @metadata.setter
    def metadata(self, metadata: Mapping):
        """Set new metadata

        Args:
            metadata (Mapping): new metadata object
        """
        self._metadata = metadata

    def column(self, indexOrName: Union[str, int]) -> Mapping:
        if indexOrName not in self._columnNames:
            raise ValueError(
                f"{indexOrName} not in BiocFrame column names {self._columnNames}"
            )

        if isinstance(indexOrName, str):
            return self._data[indexOrName]
        elif isinstance(indexOrName, int):
            return self._data[self._columnNames[indexOrName]]
        else:
            raise TypeError(
                "Unkown Type for `indexOrName`, must be either string or index"
            )

    def _slice(
        self,
        rowIndicesOrNames: Optional[Union[Sequence[int], Sequence[str]]] = None,
        colIndicesOrNames: Optional[Union[Sequence[int], Sequence[str]]] = None,
    ) -> "BiocFrame":
        """Internal method to slice BiocFrame by index or values

        Args:
            rowIndicesOrVals (Optional[Union[Sequence[int], Sequence[str]]], optional): row indices or vals to keep. Defaults to None.
            colIndicesOrVals (Optional[Union[Sequence[int], Sequence[str]]], optional): column indices or vals to keep. Defaults to None.

        Returns:
            DataFrame: sliced `BiocFrame` object
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

                if isinstance(new_column_indices, slice):
                    new_rowNames = new_rowNames[new_row_indices]
                elif isinstance(new_column_indices, list):
                    new_rowNames = [new_rowNames[i] for i in new_row_indices]
                else:
                    raise TypeError("Row Slice: Unknown match_to_indices type")

            # since row names are not set, the
            # only option here is to slice by index
            if isinstance(new_row_indices, slice) or all(
                [isinstance(k, int) for k in new_row_indices]
            ):
                for k, v in new_data.items():
                    new_data[k] = v[new_row_indices]

        return BiocFrame(
            data=new_data, rowNames=new_rowNames, columnNames=new_columnNames
        )

    # TODO: implement inplace, view
    def __getitem__(
        self, args: Union[Sequence[str], Tuple[Sequence, Optional[Sequence]]]
    ) -> "BiocFrame":
        """Subset a BiocFrame

        Slices can provided as a list of indices
        e.g.:

        Args:
            args (Union[Sequence[str], Tuple[Sequence, Optional[Sequence]]]): indices to slice.
                Sequence[str]: Slice by column names
                Tuple[Sequence, Optional[Sequence]]]: slice by indices along the row and column axes.

        Raises:
            Exception: Too many slices provided

        Returns:
            BiocFrame: new BiocFrame object
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
            all_strs = all([isinstance(k, "str") for k in args])
            if all_strs:
                return self._slice(None, args)
            else:
                raise Exception(f"provided `args` is not a list of column names")

        # tuple
        if isinstance(args, tuple):
            if len(args) == 1:
                return self._slice(args[0], None)
            elif len(args) == 2:
                return self._slice(args[0], args[1])

            raise Exception(f"`args` has too many dimensions: {len(args)}")

        raise TypeError(
            f"`args` is not supported, must to a `str`, `int`, `tuple`, `list`"
        )

    def hasColumn(self, name: str) -> bool:
        """Is column in BiocFrame?

        Args:
            name (str): column name

        Returns:
            bool: Whether the column exists in the BiocFrame
        """
        return name in self._columnNames

    def __setitem__(self, key: str, newvalue: Sequence[Any]):
        """Set/Assign a value to a column

        Args:
            key (str): Column name to set, use dot notation for nested structures
            newvalue (List[Any]): new value to set
        """
        if len(newvalue) != self._numberOfRows:
            raise Exception(
                f"new column:{key} has incorrect number of values. need to be {self._numberOfRows} but provided {len(newvalue)}"
            )

        self._data[key] = newvalue

        if key not in self._columnNames:
            self._columnNames.append(key)
            self._numberOfColumns += 1

    @staticmethod
    def fromPandas(data: pd.DataFrame) -> "BiocFrame":
        """Construct new `BiocFrame` from a `Pandas.DataFrame` object

        Args:
            data (pd.DataFrame): Pandas DataFrame object

        Returns:
            BiocFrame: a BiocFrame object
        """
        rdata = data.to_dict("list")
        rindex = None

        if data.index:
            rindex = data.index.to_list()

        # TODO: there are other things to access from the pandas object
        return BiocFrame(data=rdata, rowNames=rindex)

    def toPandas(self) -> pd.DataFrame:
        """Transform `BiocFrame` as `Pandas.DataFrame` object

        Returns:
            pd.DataFrame: a Pandas Dataframe object
        """
        return pd.DataFrame(
            data=self._data, index=self._rowNames, columns=self._columnNames
        )

    # TODO: very primilimary implementation, probably a lot more to do here
    def __array_ufunc__(self, func, method, *inputs, **kwargs) -> "BiocFrame":
        """Interface with numpy array methods

        Usage:
            np.sqrt(bioframe)

        Raises:
            Exception: Input not supported

        Returns:
            BiocFrame: BiocFrame after the function is applied
        """

        input = inputs[0]
        if not isinstance(input, BiocFrame):
            raise Exception("input not supported")

        for col in self._columnNames:
            if pd.api.types.is_numeric_dtype(pd.Series(input.column(col))):
                new_col = getattr(func, method)(input.column(col), **kwargs)
                input[col] = new_col

        return input
