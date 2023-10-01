from collections import OrderedDict
from typing import Any, Dict, List, Optional, Tuple, Union

from biocgenerics import combine
from prettytable import PrettyTable

from ._type_checks import is_list_of_type
from ._validators import validate_cols, validate_rows, validate_unique_list
from .types import SlicerArgTypes, SlicerTypes
from .utils import _match_to_indices, _slice_or_index

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


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

    def __iter__(self):
        return self

    def __next__(self):
        if self._current_index < len(self._bframe):
            iter_row_index = (
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

    Attributes:
        data (Dict[str, Any], optional): Dictionary of column names as `keys` and
            their values. All columns must have the same length. Defaults to {}.
        number_of_rows (int, optional): Number of rows.
        row_names (List, optional): Row index names.
        column_names (List[str], optional): Column names, if not provided,
            they are automatically inferred from the data.
        metadata (dict): Additional metadata. Defaults to {}.

    Raises:
        ValueError: If there is a mismatch in the number of rows or columns in the data.
    """

    def __init__(
        self,
        data: Optional[Dict[str, Any]] = None,
        number_of_rows: Optional[int] = None,
        row_names: Optional[List] = None,
        column_names: Optional[List[str]] = None,
        metadata: Optional[dict] = None,
    ) -> None:
        """Initialize a `BiocFrame` object.

        Args:
            data (Dict[str, Any], optional): Dictionary of column names as `keys` and
            their values. All columns must have the same length. Defaults to None.
            number_of_rows (int, optional): Number of rows. Defaults to None.
            row_names (List, optional): Row index names. Defaults to None.
            column_names (List[str], optional): Column names, if not provided,
                they are automatically inferred from the data. Defaults to None.
            metadata (dict, optional): Additional metadata. Defaults to None.
        """
        self._number_of_rows = number_of_rows
        self._row_names = row_names
        self._data = {} if data is None else data
        self._column_names = column_names
        self._metadata = {} if metadata is None else metadata

        self._validate()

    def _validate(self):
        """Internal method used to validate the object.

        Raises:
            ValueError: If all columns do not contain the same number of rows.
            ValueError: If row names are not unique.
        """

        if not isinstance(self._data, dict):
            raise TypeError("`data` must be a dictionary.")

        self._number_of_rows = validate_rows(
            self._data, self._number_of_rows, self._row_names
        )
        self._column_names, self._data = validate_cols(self._column_names, self._data)

        self._number_of_columns = len(self._column_names)

        if self._number_of_rows is None:
            self._number_of_rows = 0

    def __repr__(self) -> str:
        table = PrettyTable(padding_width=1)
        table.field_names = [str(col) for col in self.column_names]

        _rows = []
        rows_to_show = 2
        _top = self.shape[0]
        if _top > rows_to_show:
            _top = rows_to_show

        # top three rows
        for r in range(_top):
            _row = self.row(r)
            vals = list(_row.values())
            res = [str(v) for v in vals]
            _rows.append(res)

        if self.shape[0] > 2 * rows_to_show:
            # add ...
            _rows.append(["..." for _ in range(len(self.column_names))])

        _last = self.shape[0] - _top
        if _last <= rows_to_show:
            _last = self.shape[0] - _top

        # last three rows
        for r in range(_last + 1, len(self)):
            _row = self.row(r)
            vals = list(_row.values())
            res = [str(v) for v in vals]
            _rows.append(res)

        table.add_rows(_rows)

        pattern = (
            f"BiocFrame with {self.dims[0]} rows & {self.dims[1]} columns \n"
            f"contains row names?: {self.row_names is not None} \n"
            f"{table.get_string()}"
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
    def row_names(self) -> Optional[List]:
        """Access row names.

        Returns:
            (List, optional): Row names if available, otherwise None.
        """
        return self._row_names

    @row_names.setter
    def row_names(self, names: Optional[List]):
        """Set a new row index. All values in ``names`` must be unique.

        Args:
            names (List[str], optional): A list of unique values.

        Raises:
            ValueError: If the length of ``names`` does not match the number of rows.
            ValueError: If ``names`` is not unique.
        """

        if names is not None:
            if len(names) != self.shape[0]:
                raise ValueError(
                    "Length of `names` does not match the number of rows, need to be "
                    f"{self.shape[0]} but provided {len(names)}."
                )

            if not validate_unique_list(names):
                raise ValueError("row index must be unique!")

        self._row_names = names

    @property
    def data(self) -> Dict[str, Any]:
        """Access data as :py:class:`dict`.

        Returns:
            Dict[str, Any]: Dictionary of columns and their values.
        """
        return self._data

    @property
    def column_names(self) -> List[str]:
        """Access column names.

        Returns:
            List[str]: A list of column names.
        """
        return self._column_names

    @column_names.setter
    def column_names(self, names: List[str]):
        """Set new column names. New names must be unique.

        Args:
            names (List[str]): A list of unique values.

        Raises:
            ValueError:
                If the length of ``names`` does not match the number of columns.
                If ``names`` is not unique.
        """

        if names is None:
            raise ValueError("`names` cannot be `None`!")

        if len(names) != self._number_of_columns:
            raise ValueError(
                "Length of `names` does not match number of columns, need to be "
                f"{self._number_of_columns} but provided {len(names)}."
            )

        if not (validate_unique_list(names)):
            raise ValueError("Column names must be unique!")

        new_data = OrderedDict()
        for idx in range(len(names)):
            new_data[names[idx]] = self._data[self.column_names[idx]]

        self._column_names = names
        self._data = new_data

    @property
    def metadata(self) -> dict:
        """Access metadata.

        Returns:
            dict: Metadata object.
        """
        return self._metadata

    @metadata.setter
    def metadata(self, metadata: dict):
        """Set new metadata.

        Args:
            metadata (dict): New metadata object.
        """
        if not isinstance(metadata, dict):
            raise TypeError(
                f"`metadata` must be a dictionary, provided {type(metadata)}."
            )

        self._metadata = metadata

    def has_column(self, name: str) -> bool:
        """Checks whether the column exists.

        Args:
            name (str): Name to check.

        Returns:
            bool: True if the column exists, otherwise False.
        """
        return name in self.column_names

    def column(self, index_or_name: Union[str, int]) -> Any:
        """Access a column by integer position or column label.

        Args:
            index_or_name (Union[str, int]): Name of the column, which must a valid name in
                :py:attr:`~biocframe.BiocFrame.BiocFrame.column_names`.

                Alternatively, you may provide the integer index of the column to access.

        Raises:
            ValueError:
                If ``index_or_name`` is not in column names.
                If the integer index is greater than the number of columns.
            TypeError:
                If ``index_or_name`` is neither a string nor an integer.

        Returns:
            Any: Column with its original type preserved.
        """

        if not isinstance(index_or_name, (int, str)):
            raise TypeError(
                "`index_or_name` must be either an integer index or column name."
            )

        return self[None, index_or_name]

    def row(self, index_or_name: Union[str, int]) -> dict:
        """Access a row by integer position or row name.

        Args:
            index_or_name (Union[str, int]): Integer index of the row to access.

                Alternatively, you may provide a string specifying the row to access,
                only if :py:attr:`~biocframe.BiocFrame.BiocFrame.row_names` are available.

        Raises:
            ValueError:
                If ``index_or_name`` is not in row names.
                If the integer index is greater than the number of rows.
            TypeError:
                If ``index_or_name`` is neither a string nor an integer.

        Returns:
            dict: A dictionary with keys as column names and their values.
        """

        if not isinstance(index_or_name, (int, str)):
            raise TypeError(
                "`index_or_name` must be either an integer index or row name."
            )

        return self[index_or_name, None]

    def _slice(
        self,
        row_indices_or_names: Optional[SlicerTypes] = None,
        column_indices_or_names: Optional[SlicerTypes] = None,
    ) -> Union["BiocFrame", dict, list]:
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

        new_data = OrderedDict()
        new_row_names = self.row_names
        new_column_names = self.column_names
        is_row_unary = False
        is_col_unary = False

        # slice the columns and data
        if column_indices_or_names is not None:
            new_column_indices, is_col_unary = _match_to_indices(
                self.column_names, column_indices_or_names
            )

            new_column_names = _slice_or_index(new_column_names, new_column_indices)

        for col in new_column_names:
            new_data[col] = self._data[col]

        # slice the rows of the data
        new_number_of_rows = None
        if row_indices_or_names is not None:
            temp_row_names = self.row_names
            if temp_row_names is None:
                temp_row_names = list(range(self.shape[0]))

            new_row_indices, is_row_unary = _match_to_indices(
                temp_row_names, row_indices_or_names
            )

            new_row_names = _slice_or_index(temp_row_names, new_row_indices)
            new_number_of_rows = len(new_row_names)

            for k, v in new_data.items():
                if hasattr(v, "shape"):
                    tmp = [slice(None)] * len(v.shape)
                    tmp[0] = new_row_indices
                    new_data[k] = v[(*tmp,)]
                else:
                    new_data[k] = _slice_or_index(v, new_row_indices)
        else:
            new_number_of_rows = self.shape[0]

        if is_row_unary is True:
            rdata = {}
            for col in new_column_names:
                rdata[col] = new_data[col][0]
            return rdata
        elif is_col_unary is True:
            return new_data[new_column_names[0]]

        current_class_const = type(self)
        return current_class_const(
            data=new_data,
            number_of_rows=new_number_of_rows,
            row_names=new_row_names,
            column_names=new_column_names,
        )

    # TODO: implement in-place or views
    def __getitem__(
        self,
        args: SlicerArgTypes,
    ) -> Union["BiocFrame", dict, list]:
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
        if isinstance(args, str):
            return self._slice(None, args)

        if isinstance(args, int):
            return self._slice(args, None)

        # not an array, a slice
        if isinstance(args, slice):
            return self._slice(args, None)

        if isinstance(args, list):
            # column names if everything is a string
            if is_list_of_type(args, str):
                return self._slice(None, args)
            elif is_list_of_type(args, int):
                return self._slice(args, None)
            else:
                raise ValueError("`args` is not supported.")

        # tuple
        if isinstance(args, tuple):
            if len(args) == 0:
                raise ValueError("`args` must contain at least one slice.")

            if len(args) == 1:
                return self._slice(args[0], None)
            elif len(args) == 2:
                return self._slice(
                    args[0],
                    args[1],
                )
            else:
                raise ValueError("Length of `args` is more than 2.")

        raise TypeError("`args` is not supported.")

    # TODO: implement in-place or views
    def __setitem__(self, name: str, value: List):
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
        if len(value) != self.shape[0]:
            raise ValueError(
                "Length of `value`, does not match the number of the rows,"
                f"need to be {self.shape[0]} but provided {len(value)}."
            )

        if name not in self.column_names:
            self._column_names.append(name)
            self._number_of_columns += 1

        self._data[name] = value

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

        del self._data[name]
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

    def to_pandas(self):
        """Convert :py:class:`~biocframe.BiocFrame.BiocFrame` into :py:class:`~pandas.DataFrame` object.

        Returns:
            DataFrame: A :py:class:`~pandas.DataFrame` object.
        """
        from pandas import DataFrame

        return DataFrame(
            data=self._data, index=self._row_names, columns=self._column_names
        )

    # TODO: very primitive implementation, needs very robust testing
    # TODO: implement in-place, view
    def __array_ufunc__(self, func, method, *inputs, **kwargs) -> "BiocFrame":
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

        from pandas import Series
        from pandas.api.types import is_numeric_dtype

        input = inputs[0]
        if not isinstance(input, BiocFrame):
            raise TypeError("Input is not a `BiocFrame` object.")

        for col in self.column_names:
            if is_numeric_dtype(Series(input.column(col))):
                new_col = getattr(func, method)(input.column(col), **kwargs)
                input[col] = new_col

        return input

    # compatibility with Pandas
    @property
    def columns(self) -> list:
        """Alias to :py:meth:`~biocframe.BiocFrame.BiocFrame.column_names`.

        Returns:
            list: List of column names.
        """
        return self.column_names

    @property
    def index(self) -> Optional[list]:
        """Alias to :py:meth:`~biocframe.BiocFrame.BiocFrame.row_names`.

        Returns:
            (list, optional): List of row names if available, otherwise None.
        """
        return self.row_names

    # compatibility with R interfaces
    @property
    def rownames(self) -> Optional[list]:
        """Alias to :py:meth:`~biocframe.BiocFrame.BiocFrame.row_names`.

        Returns:
            (list, optional): List of row names if available, otherwise None.
        """
        return self.row_names

    @rownames.setter
    def rownames(self, names: list):
        """Alias to :py:meth:`~biocframe.BiocFrame.BiocFrame.row_names`.

        Args:
            names (list): New row names.
        """
        self.row_names = names

    @property
    def colnames(self) -> list:
        """Alias to :py:meth:`~biocframe.BiocFrame.BiocFrame.column_names`.

        Returns:
            list: list of column names.
        """
        return self.column_names

    @colnames.setter
    def colnames(self, names: list):
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

    def combine(self, *other: "BiocFrame") -> "BiocFrame":
        if not is_list_of_type(other, BiocFrame):
            raise TypeError("All objects to combine must be BiocFrame objects.")

        all_objects = [self] + list(other)

        all_columns = [x.column_names for x in all_objects]
        all_columns.append(self.column_names)
        all_unique_columns = list(
            set([item for sublist in all_columns for item in sublist])
        )

        all_row_names = [None] * len(self) if self.row_names is None else self.row_names
        all_num_rows = sum([len(x) for x in all_objects])
        all_data = self.data.copy()
        for obj in other:
            for ocol in all_unique_columns:
                if ocol not in all_data:
                    all_data[ocol] = [None] * len(obj)

                if ocol not in obj.column_names:
                    all_data[ocol] = [None] * len(obj)
                else:
                    all_data[ocol] = combine(all_data[ocol], obj.column(ocol))

            rnames = obj.row_names
            if rnames is None:
                rnames = [None] * len(obj)

            all_row_names.extend(rnames)

        if all([x is None for x in all_row_names]) or len(all_row_names) == 0:
            all_row_names = None

        current_class_const = type(self)
        return current_class_const(
            all_data,
            number_of_rows=all_num_rows,
            row_names=all_row_names,
            column_names=all_unique_columns,
        )
