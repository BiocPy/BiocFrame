"""A Bioconductor-like data frame."""

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
    cast,
    overload,
)

from pandas.api.types import is_numeric_dtype  # type: ignore
from prettytable import PrettyTable

from ._type_checks import is_list_of_type
from ._validators import validate_cols, validate_rows, validate_unique_list
from .types import (
    AllSlice,
    AtomicSlice,
    BiocCol,
    ColSlice,
    ColType,
    DataType,
    RowSlice,
    SeqSlice,
    SimpleSlice,
    TupleSlice,
)
from .utils import match_to_indices, slice_or_index

try:
    from pandas import DataFrame, Series
except ImportError:
    pass

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"

ItemType = Union["BiocFrame", ColType]


class BiocFrameIter:
    """An iterator to a :py:class:`~biocframe.BiocFrame.BiocFrame` object.

    Args:
        obj (BiocFrame): Source object to iterate.
    """

    def __init__(self, obj: "BiocFrame") -> None:
        """Initialize the iterator.

        Args:
            obj (BiocFrame): source object to iterate.
        """
        self._bframe = obj
        self._current_index = 0

    def __iter__(self) -> "BiocFrameIter":
        return self

    def __next__(self):
        if self._current_index < len(self._bframe):
            iter_row_index: Optional[str] = (
                self._bframe.row_names[self._current_index]
                if self._bframe.row_names is not None
                else None
            )

            iter_slice = self._bframe.row(self._current_index)
            self._current_index += 1
            return (iter_row_index, iter_slice)

        raise StopIteration


class BiocFrame:
    """`BiocFrame` is an alternative to :class:`~pandas.DataFrame`.

    Columns are required to implement the length (``__len__``) and slice (``__getitem__``) dunder
    methods. This allows :py:class:`~biocframe.BiocFrame.BiocFrame` to accept nested
    `BiocFrame` objects as columns.

    Typical usage example:

    To create a **BiocFrame** object, simply provide the data as a dictionary.

    .. code-block:: python

        # made up ensembl ids.
        obj = {
            "ensembl": ["ENS00001", "ENS00002", "ENS00002"],
            "symbol": ["MAP1A", "BIN1", "ESR1"],
        }
        bframe = BiocFrame(obj)

    Alternatively, you can specify :py:class:`~biocframe.BiocFrame.BiocFrame` class
    as a column.

    .. code-block:: python

        # made up chromosome locations and ensembl ids.
        obj = {
            "ensembl": ["ENS00001", "ENS00002", "ENS00002"],
            "symbol": ["MAP1A", "BIN1", "ESR1"],
            "ranges": BiocFrame({
                "chr": ["chr1", "chr2", "chr3"]
                "start": [1000, 1100, 5000],
                "end": [1100, 4000, 5500]
            ),
        }
        bframe = BiocFrame(obj)

    Methods are also available to slice the object

    .. code-block:: python

        sliced_bframe = bframe[1:2, [True, False, False]]
    """

    def __init__(
        self,
        data: Optional[DataType] = None,
        number_of_rows: Optional[int] = None,
        row_names: Optional[List[str]] = None,
        column_names: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a `BiocFrame` object.

        Args:
            data (Dict[str, Union[List, Dict, BioSeq]], optional):
                Dictionary of column names as `keys` and their values. all columns must have
                the same length. Defaults to None.
            number_of_rows (int, optional): Number of rows. Defaults to None.
            row_names (List, optional): Row index names. Defaults to None.
            column_names (List[str], optional): Column names, if not provided,
                is automatically inferred from data keys. Defaults to None.
            metadata (Dict, optional): Additional metadata. Defaults to None.

        Raises:
            ValueError: If all columns do not contain the same number of rows.
            ValueError: If row names are not unique.
        """
        self._data: DataType = {} if data is None else data
        self._row_names = row_names
        self._number_of_rows = validate_rows(
            self._data, number_of_rows, self._row_names
        )
        self._column_names, self._data = validate_cols(
            column_names, self._data
        )
        self._number_of_columns = len(self._column_names)
        self._metadata = {} if metadata is None else metadata

    def __repr__(self) -> str:
        """Get a machine-readable string representation of the object."""
        table = PrettyTable(padding_width=1)
        table.field_names = [str(col) for col in self._column_names]

        num_rows = self.shape[0]
        # maximum number of top and bottom rows to show
        max_shown_rows = 3

        max_top_row = max_shown_rows if num_rows > max_shown_rows else num_rows

        min_last_row = num_rows - max_shown_rows
        if min_last_row <= 0:
            min_last_row = None
        elif min_last_row < max_top_row:
            min_last_row = max_top_row

        rows: List[List[str]] = []

        # up to top three rows
        for r in range(max_top_row):
            rows.append([str(val) for val in self.row(r).values()])

        if min_last_row is not None:
            if num_rows > (max_shown_rows * 2):
                # add ... to the middle row
                rows.append(["..." for _ in range(len(self._column_names))])

            # up to last three rows
            for r in range(min_last_row, num_rows):
                rows.append([str(val) for val in self.row(r).values()])

        table.add_rows(rows)  # type: ignore

        pattern = (
            f"BiocFrame with {num_rows} rows & {self.dims[1]} columns \n"
            f"with row names: {self.row_names is not None} \n"
            f"{table.get_string()}"  # type: ignore
        )

        return pattern

    @property
    def shape(self) -> Tuple[int, int]:
        """Get shape of the data frame.

        Returns:
            Tuple[int, int]: A tuple  (m, n),
            where `m` is the number of rows, and `n` is the number of columns.
        """
        return (self._number_of_rows, self._number_of_columns)

    @property
    def row_names(self) -> Optional[List[str]]:
        """Get/set the row names.

        Set new row index. All values in ``names`` must be unique.

        Args:
            names (List, optional): A list of unique values, or `None`. If
            `None` row names are removed.

        Returns:
            (List, optional): Row names if available, else None.

        Raises:
            ValueError: If the length of ``names`` does not match the number of rows.
            ValueError: If ``names`` is not unique.
        """
        return self._row_names

    @row_names.setter
    def row_names(self, names: Optional[List[str]]) -> None:
        if names is not None:
            if len(names) != self.shape[0]:
                raise ValueError(
                    "Length of `names` does not match the number of rows, "
                    f"need to be {self.shape[0]} but provided {len(names)}."
                )

            if not validate_unique_list(names):
                raise ValueError("row index must be unique!")

        self._row_names = names

    @property
    def data(self) -> DataType:
        """Access data as :py:class:`dict`.

        Returns:
            Dict[str, Union[List, Dict]]:
                Dictionary of columns and their values.
        """
        return self._data

    @property
    def column_names(self) -> List[str]:
        """Get/set the column_names.

        Args:
            names (List[str]): A list of unique values.

        Returns:
            list: A list of column names.

        Raises:
            ValueError:
                If the length of ``names`` does not match the number of columns.
                If ``names`` is not unique.
        """
        return self._column_names

    @column_names.setter
    def column_names(self, names: List[str]) -> None:
        if len(names) != self._number_of_columns:
            raise ValueError(
                "Length of `names` does not match number of columns. Needs to "
                f"be {self._number_of_columns} but provided {len(names)}."
            )

        if not (validate_unique_list(names)):
            raise ValueError("Column names must be unique!")

        self._column_names = names
        self._data = {
            names[i]: v for i, (_, v) in enumerate(self.data.items())
        }

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get/set the metadata.

        Args:
            metadata (Dict, Optional): New metadata object.

        Returns:
            dict: Metadata object.
        """
        return self._metadata

    @metadata.setter
    def metadata(self, metadata: Dict[str, Any]):
        self._metadata = metadata

    def has_column(self, name: str) -> bool:
        """Checks whether the column exists.

        Args:
            name (str): Name to check.

        Returns:
            bool: True if the column exists, otherwise False.
        """
        return name in self.column_names

    @overload
    def _slice(
        self,
        row_indices_or_names: AtomicSlice,
        column_indices_or_names: None,
    ) -> Dict[str, Any]:
        ...

    @overload
    def _slice(
        self,
        row_indices_or_names: Optional[AllSlice],
        column_indices_or_names: Union[AllSlice, None],
    ) -> ItemType:
        ...

    def _slice(
        self,
        row_indices_or_names: Optional[AllSlice] = None,
        column_indices_or_names: Optional[AllSlice] = None,
    ) -> ItemType:
        """Internal method to slice by index or values.

        Args:
            row_indices_or_names (SlicerTypes, optional): Row indices (integer positions)
                or row names (string) to slice. Defaults to None.

            column_indices_or_names (SlicerTypes, optional): Column indices (integer positions)
                or column names (string) to slice. Defaults to None.

        Returns:
            Union["BiocFrame", dict, list]:
                - If a single row is sliced, returns a :py:class:`dict`.
                - If a single column is sliced, returns a :py:class:`list`.
                - For all other scenarios, returns the same type as the caller with the subsetted rows and columns.
        """
        new_row_names = self.row_names
        new_column_names = self.column_names
        is_row_unary = False
        is_col_unary = False

        # slice the columns and data
        if column_indices_or_names is not None:
            new_column_indices, is_col_unary = match_to_indices(
                self.column_names, column_indices_or_names
            )

            new_column_names = cast(
                List[str], slice_or_index(new_column_names, new_column_indices)
            )

        new_data = {col: self._data[col] for col in new_column_names}

        # slice the rows of the data
        new_number_of_rows = None
        if row_indices_or_names is not None:
            temp_row_names = self.row_names
            if temp_row_names is None:
                temp_row_names = list(range(self.shape[0]))

            new_row_indices, is_row_unary = match_to_indices(
                temp_row_names, row_indices_or_names
            )

            new_row_names = slice_or_index(temp_row_names, new_row_indices)
            new_number_of_rows = len(new_row_names)

            for k, v in new_data.items():
                if isinstance(v, BiocCol):
                    tmp: List[SimpleSlice] = [slice(None)] * len(v.shape)
                    tmp[0] = new_row_indices
                    new_data[k] = v[(*tmp,)]
                else:
                    new_data[k] = slice_or_index(v, new_row_indices)
        else:
            new_number_of_rows = self.shape[0]

        if is_row_unary is True:
            return {
                col: next(
                    iter(
                        new_data[col].values()  # type: ignore
                        if isinstance(new_data[col], dict)
                        else new_data[col]
                    )
                )
                for col in new_column_names
            }

        if is_col_unary is True:
            return new_data[new_column_names[0]]

        return type(self)(
            data=new_data,
            number_of_rows=new_number_of_rows,
            row_names=new_row_names,
            column_names=new_column_names,
        )

    @overload
    def __getitem__(self, __key: Union[SeqSlice, slice, ColSlice]) -> ItemType:
        ...

    @overload
    def __getitem__(
        self, __key: Union[AtomicSlice, RowSlice]
    ) -> Dict[str, Any]:
        ...

    @overload
    def __getitem__(self, __key: TupleSlice) -> "BiocFrame":
        ...

    # TODO: implement in-place or views
    def __getitem__(self, __key: AllSlice) -> ItemType:
        """Subset the data frame.

        This operation returns a new object with the same type as the caller.
        If you need to access specific rows or columns, use the
        :py:meth:`~biocframe.BiocFrame.BiocFrame.row` or
        :py:meth:`~biocframe.BiocFrame.BiocFrame.column`
        methods.

        Usage:

        .. code-block:: python

            # made up chromosome locations and ensembl ids.
            obj = {
                "ensembl": ["ENS00001", "ENS00002", "ENS00002"],
                "symbol": ["MAP1A", "BIN1", "ESR1"],
                "ranges": BiocFrame({
                    "chr": ["chr1", "chr2", "chr3"],
                    "start": [1000, 1100, 5000],
                    "end": [1100, 4000, 5500]
                }),
            }
            bframe = BiocFrame(obj)

            # Different ways to slice.

            bframe[0:2, 0:2]
            bframe[[0, 2], [True, False, False]]
            bframe[<List of column names>]

        Args:
            args (SlicerArgTypes): A Tuple of slicer arguments to subset rows and
                columns. An element in ``args`` may be,

                - List of booleans, True to keep the row/column, False to remove.
                    The length of the boolean vector must be the same as the number of rows/columns.

                - List of integer positions along rows/columns to keep.

                - A :py:class:`slice` object specifying the list of indices to keep.

                - A list of index names to keep. For rows, the object must contain unique
                    :py:attr:`~biocframe.BiocFrame.BiocFrame.row_names`, and for columns must
                    contain unique :py:attr:`~biocframe.BiocFrame.BiocFrame.column_names`.

                - An integer to subset either a single row or column index.
                    Alternatively, you might want to use
                    :py:meth:`~biocframe.BiocFrame.BiocFrame.row` or
                    :py:meth:`~biocframe.BiocFrame.BiocFrame.column` methods.

                - A string to subset either a single row or column by label.
                    Alternatively, you might want to use
                    :py:meth:`~biocframe.BiocFrame.BiocFrame.row` or
                    :py:meth:`~biocframe.BiocFrame.BiocFrame.column` methods.

        Raises:
            ValueError: If too many slices are provided.
            TypeError: If the provided ``args`` are not of the expected type.

        Returns:
            Union["BiocFrame", dict, list]:
            - If a single row is sliced, returns a :py:class:`dict`.
            - If a single column is sliced, returns a :py:class:`list`.
            - For all other scenarios, returns the same type as the caller with the subsetted rows and columns.
        """
        # not an array, single str, slice by column
        if isinstance(__key, str):
            return self._slice(None, __key)

        if isinstance(__key, bool):
            return self._slice(__key, None)

        if isinstance(__key, int):
            return self._slice(__key, None)

        # not an array, a slice
        if isinstance(__key, slice):
            return self._slice(__key, None)

        if isinstance(__key, list):
            # column names if everything is a string
            if is_list_of_type(__key, str):
                return self._slice(None, __key)

            if is_list_of_type(__key, int):
                return self._slice(__key, None)

            if is_list_of_type(__key, bool):
                return self._slice(__key, None)

            raise ValueError("`args` is not supported.")

        # tuple of two elements
        if len(__key) != 2:
            raise ValueError("Length of `args` is more than 2.")

        return self._slice(__key[0], __key[1])

    def column(self, index_or_name: AtomicSlice) -> ItemType:
        """Access a column by integer position or column label.

        Args:
            index_or_name (Union[str, int]): Name of the column, must be present in
                :py:attr:`~biocframe.BiocFrame.BiocFrame.column_names`.

                Alternatively, you may provide the integer index of the column to
                access.

        Raises:
            ValueError: if ``index_or_name`` is not in column names.
            ValueError: if integer index is greater than number of columns.
            TypeError: if ``index_or_name`` is neither a string nor an integer.

        Returns:
            Any: Column with its original type preserved.
        """
        return self[:, index_or_name]

    def row(self, index_or_name: AtomicSlice) -> Dict[str, Any]:
        """Access a row by integer position or row name.

        Args:
            index_or_name (Union[str, int]): Integer index of the row to access.

                Alternatively, you may provide a string specifying the row to access,
                only if :py:attr:`~biocframe.BiocFrame.BiocFrame.row_names` are
                available.

        Raises:
            ValueError: if ``index_or_name`` not in row names.
            ValueError: if integer index greater than number of rows.
            TypeError: if ``index_or_name`` is neither a string nor an integer.

        Returns:
            Any: A dictionary with keys as column names and their values.
        """
        return self[index_or_name, :]

    # TODO: implement in-place or views
    def __setitem__(self, __key: str, __value: ColType) -> None:
        """Add or re-assign a value to a column.

        Usage:

        .. code-block:: python

            # Made-up chromosome locations and ensembl ids.
            obj = {
                "ensembl": ["ENS00001", "ENS00002", "ENS00002"],
                "symbol": ["MAP1A", "BIN1", "ESR1"],
                "ranges": BiocFrame({
                    "chr": ["chr1", "chr2", "chr3"],
                    "start": [1000, 1100, 5000],
                    "end": [1100, 4000, 5500]
                }),
            }
            bframe = BiocFrame(obj)

            bframe["symbol"] = ["gene_a", "gene_b", "gene_c"]

        Args:
            name (str): Name of the column.
            value (List): New value to set.

        Raises:
            ValueError: If the length of ``value`` does not match the number of rows.
        """
        if len(__value) != self.shape[0]:
            raise ValueError(
                "Length of `value`, does not match the number of the rows,"
                f"need to be {self.shape[0]} but provided {len(__value)}."
            )

        if __key not in self.column_names:
            self._column_names.append(__key)
            self._number_of_columns += 1

        # Dunno how to fix this one...
        self._data[__key] = __value  # type: ignore

    # TODO: implement in-place or view
    def __delitem__(self, name: str):
        """Remove a column.

        Usage:

        .. code-block:: python

            # made-up chromosome locations and ensembl ids.
            obj = {
                "ensembl": ["ENS00001", "ENS00002", "ENS00002"],
                "symbol": ["MAP1A", "BIN1", "ESR1"],
                "ranges": BiocFrame({
                    "chr": ["chr1", "chr2", "chr3"],
                    "start": [1000, 1100, 5000],
                    "end": [1100, 4000, 5500]
                }),
            }
            bframe = BiocFrame(obj)
            delete bframe["symbol"]

        Args:
            name (str): Name of the column.

        Raises:
            ValueError: If `name` is not a valid column.
        """
        if name not in self.column_names:
            raise ValueError(f"Column: '{name}' does not exist.")

        try:
            del self._data[name]  # type: ignore
        except Exception:
            self._data = {k: v for k, v in self._data.items() if k != name}

        self._column_names.remove(name)
        self._number_of_columns -= 1

    def __len__(self) -> int:
        """Number of rows.

        Returns:
            int: Number of rows.
        """
        return self.shape[0]

    def __iter__(self) -> BiocFrameIter:
        """Iterator over rows."""
        return BiocFrameIter(self)

    def to_pandas(self) -> "DataFrame":
        """Convert :py:class:`~biocframe.BiocFrame.BiocFrame` to a :py:class:`~pandas.DataFrame` object.

        Returns:
            DataFrame: A :py:class:`~pandas.DataFrame` object.
        """
        return DataFrame(
            data=self._data, index=self._row_names, columns=self._column_names
        )

    # TODO: very primitive implementation, needs very robust testing
    # TODO: implement in-place, view
    def __array_ufunc__(
        self, ufunc: Any, method: str, *inputs: Any, **kwargs: Any
    ) -> "BiocFrame":
        """Interface with NumPy array methods.

        Usage:

        .. code-block:: python

            np.sqrt(biocframe)

        Raises:
            TypeError: If ``input`` is not a :py:class:`~biocframe.BiocFrame.BiocFrame`
            object.

        Returns:
            An object with the same type as the caller.
        """
        _input = inputs[0]
        if not isinstance(_input, BiocFrame):
            raise TypeError("Input is not a `BiocFrame` object.")

        for col in self.column_names:
            if is_numeric_dtype(Series(_input.column(col))):  # type: ignore
                new_col = getattr(ufunc, method)(_input.column(col), **kwargs)
                _input[col] = new_col

        return _input

    ###########################################################################
    # compatibility with Pandas
    @property
    def columns(self) -> List[str]:
        """Alias to :py:meth:`~biocframe.BiocFrame.BiocFrame.column_names`.

        Returns:
            list: List of column names.
        """
        return self.column_names

    @property
    def index(self) -> Optional[List[str]]:
        """Alias to :py:meth:`~biocframe.BiocFrame.BiocFrame.row_names`.

        Returns:
            (list, optional): List of row names if available, otherwise None.
        """
        return self.row_names

    ###########################################################################
    # compatibility with R interfaces
    @property
    def rownames(self) -> Optional[List[str]]:
        """Alias to :py:meth:`~biocframe.BiocFrame.BiocFrame.row_names`.

        Returns:
            (list, optional): List of row names if available, otherwise None.
        """
        return self.row_names

    @rownames.setter
    def rownames(self, names: List[str]):
        """Alias to :py:meth:`~biocframe.BiocFrame.BiocFrame.row_names`.

        Args:
            names (list): New row names.
        """
        self.row_names = names

    @property
    def colnames(self) -> List[str]:
        """Alias to :py:meth:`~biocframe.BiocFrame.BiocFrame.column_names`.

        Returns:
            list: list of column names.
        """
        return self.column_names

    @colnames.setter
    def colnames(self, names: List[str]):
        """Alias to :py:meth:`~biocframe.BiocFrame.BiocFrame.column_names`.

        Args:
            names (list): New column names.
        """
        self.column_names = names

    @property
    def dims(self) -> Tuple[int, int]:
        """Alias to :py:meth:`~biocframe.BiocFrame.BiocFrame.shape`.

        Returns:
            Tuple[int, int]: A tuple  (m, n),
            where `m` is the number of rows, and `n` is the number of columns.
        """
        return self.shape
