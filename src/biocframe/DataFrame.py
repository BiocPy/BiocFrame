from functools import reduce
from typing import Any, Dict, List, Union
from .utils import extract_keys, _slice, slice_data
import operator
import logging
import pandas as pd


__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


class DataFrame:
    def __init__(
        self, data: Dict[str, Union[List[Any], Dict]], index: List[Any] = None
    ) -> None:
        colnames, dims = extract_keys(data)

        if len(set(dims)) != 1:
            logging.error("all columns need to have the same number of values")
            raise Exception("all columns need to have the same number of values")

        rowLength = list(set(dims))[0]

        if index is None:
            index = range(0, rowLength)

        if index is not None and rowLength != len(index):
            logging.error(
                f"dimensions do not match index:{len(index)} and data:{rowLength}"
            )
            raise Exception("dimensions do not match")

        self._all_colnames = colnames
        self._colnames = list(data.keys())
        self._rowLength = rowLength
        self._colLength = len(self._colnames)

        self._data = data
        self._index = index

    @property
    def dims(self):
        return (self._rowLength, self._colLength)

    @property
    def colnames(self):
        return self._colnames

    @colnames.setter
    def colnames(self, value: List):
        if len(value) != self._colLength:
            logging.error(
                f"Incorrect number of column names, needs to be {self._colLength} but provided {len(value)}"
            )
            raise Exception("Incorrect number of column names")

        new_data = {}
        for idx in range(len(value)):
            new_data[value[idx]] = self._data[self._colnames[idx]]

        self._colnames = value
        self._data = new_data


    def __getitem__(self, args: tuple) -> "DataFrame":
        """Subset a DataFrame

        Args:
            args (tuple): indices to slice. tuple can
                contains slices along dimensions

        Raises:
            Exception: Too many slices

        Returns:
            DataFrame: new DataFrame object
        """
        rowIndices = args[0]
        colIndices = None

        if len(args) > 1:
            colIndices = args[1]
        elif len(args) > 2:
            logging.error(
                f"too many slices, can only provide row and column slices, but provided {len(args)} "
            )
            raise Exception("contains too many slices")

        new_data = self._data
        new_index = None
        new_cols = None

        # slice the index
        if self._index is not None:
            new_index = _slice(self._index, rowIndices)

        # slice the colnames
        if colIndices is not None:
            new_cols = _slice(self._colnames, colIndices)

            new_data = {}
            for col in new_cols:
                new_data[col] = self._data[col]

        # slice the rows of the data
        if rowIndices is not None:
            new_data = slice_data(new_data, rowIndices)

        return DataFrame(new_data, new_index)

    def __setitem__(self, key: str, newvalue: List[Any]):
        """Set/Assign a value to a column

        Args:
            key (str): Column name to set, use dot notation for nested structures
            newvalue (List[Any]): new value to set
        """
        if len(newvalue) != self._rowLength:
            logging.error(
                f"new column:{key} has incorrect number of values. need to be {self._rowLength} but contains {len(newvalue)}"
            )
            raise Exception(f"Incorrect number of values")

        if key == "index":
            self._index = newvalue
        else:
            if "." in key:
                ksplits = key.split(".")
                last = reduce(operator.getitem, ksplits[:-1], self._data)
                last[ksplits[:-1]] = newvalue
            else:
                self._data[key] = newvalue

            if key not in self._all_colnames:
                self._all_colnames.append(key)
                self._rowLength += 1

    @staticmethod
    def fromPandas(data: pd.DataFrame) -> "DataFrame":
        """Create a DataFrame from a `Pandas.DataFrame` object

        Args:
            data (pd.DataFrame): Pandas DataFrame object

        Returns:
            DataFrame: DataFrame object
        """
        rdata = data.to_dict("list")
        rindex = None

        if data.index:
            rindex = data.index.to_list()

        return DataFrame(rdata, rindex)

    def toPandas(self) -> pd.DataFrame:
        """Export as `Pandas.DataFrame` object

        Returns:
            pd.DataFrame: Pandas Dataframe object
        """
        return pd.DataFrame(data=self._data, index=self._index)
