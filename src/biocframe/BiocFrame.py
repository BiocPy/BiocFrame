from collections import OrderedDict
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
from warnings import warn
from copy import copy
import numpy

import biocutils as ut

from .types import SlicerArgTypes, SlicerTypes

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def _guess_number_of_rows(
    number_of_rows: Optional[int],
    data: Dict[str, Any],
    row_names: Optional[List[str]],
):
    if number_of_rows is not None:
        return number_of_rows
    if len(data) > 0:
        return ut.get_height(next(iter(data.values())))
    if row_names is not None:
        return len(row_names)
    return 0


def _validate_rows(
    number_of_rows: int,
    data: Dict[str, Any],
    row_names: Optional[List[str]],
) -> int:
    if not isinstance(data, dict):
        raise TypeError("`data` must be a dictionary.")

    incorrect_len_keys = []
    for k, v in data.items():
        if number_of_rows != ut.get_height(v):
            incorrect_len_keys.append(k)

    if len(incorrect_len_keys) > 0:
        raise ValueError(
            "All columns in ``data`` must be the same "
            f"length, these columns do not: {', '.join(incorrect_len_keys)}."
        )

    if row_names is not None:
        if len(row_names) != number_of_rows:
            raise ValueError(
                "Length of `row_names` and `number_of_rows` do not match, "
                f"{len(row_names)} != {number_of_rows}"
            )
        if any(x is None for x in row_names):
            raise ValueError("`row_names` cannot contain None values.")


def _validate_columns(
    column_names: List[str],
    data: Dict[str, Any],
    mcols: Optional["BiocFrame"],
) -> Tuple[List[str], Dict[str, Any]]:
    if sorted(column_names) != sorted(data.keys()):
        raise ValueError("Mismatch between `column_names` and the keys of `data`.")

    if mcols is not None:
        if mcols.shape[0] != len(column_names):
            raise ValueError(
                "Number of rows in `mcols` should be equal to the number of columns."
            )


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
    """`BiocFrame` is an alternative to :class:`~pandas.DataFrame`, with support for nested and flexible column types.
    Similar to R's ``DataFrame`` class.

    Columns are required to implement the length (``__len__``) and slice (``__getitem__``) dunder
    methods. This allows :py:class:`~biocframe.BiocFrame.BiocFrame` to accept nested
    `BiocFrame` or any supported class as columns.

    Typical usage example:

    To create a **BiocFrame** object, simply provide the data as a dictionary.

    .. code-block:: python

        # made up ensembl ids.
        obj = {
            "ensembl": ["ENS00001", "ENS00002", "ENS00003"],
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
                "chr": ["chr1", "chr2", "chr3"],
                "start": [1000, 1100, 5000],
                "end": [1100, 4000, 5500]
            }),
        }
        bframe = BiocFrame(obj)

    Methods are available to **slice** (:py:meth:`~biocframe.BiocFrame.BiocFrame.__getitem__`) the object,

    .. code-block:: python

        sliced = bframe[1:2, [True, False, False]]

    Additionally, the ``slice`` operation accepts different inputs, you can either
    specify a boolean vector, a :py:class:`~slice` object, or a list of indices or row names to subset.

    To access a particular **row or column** of the dataframe,

    .. code-block:: python

        row2 = bframe.row(2)
        ensembl_col = bframe.column("ensembl")

    Use the :py:func:`~biocgenerics.combine.combine` generic to concatenate multiple biocframe objects,

    .. code-block:: python

        bframe1 = BiocFrame(
            {
                "odd": [1, 3, 5, 7, 9],
                "even": [0, 2, 4, 6, 8],
            }
        )

        bframe2 = BiocFrame(
            {
                "odd": [11, 33, 55, 77, 99],
                "even": [0, 22, 44, 66, 88],
            }
        )

        from biocgenerics.combine import combine
        combined = combine(bframe1, bframe2)

    or the combine function

    .. code-block:: python

        combined = bframe1.combine(bframe2)
    """

    def __init__(
        self,
        data: Optional[Dict[str, Any]] = None,
        number_of_rows: Optional[int] = None,
        row_names: Optional[List] = None,
        column_names: Optional[List[str]] = None,
        mcols: Optional["BiocFrame"] = None,
        metadata: Optional[dict] = None,
        validate: bool = True,
    ) -> None:
        """Initialize a `BiocFrame` object.

        Args:
            data (Dict[str, Any], optional):
                Dictionary of column names as `keys` and
                their values. All columns must have the same length. Defaults to {}.

            number_of_rows (int, optional):
                Number of rows. If not specified, inferred from ``data``.

            row_names (list, optional):
                Row names.

            column_names (list, optional):
                Column names. If not provided, inferred from the ``data``.

            mcols (BiocFrame, optional):
                Metadata about columns. Must have the same length as the number
                of columns. Defaults to None.

            metadata (dict):
                Additional metadata. Defaults to {}.

            validate (bool):
                Internal use only.
        """
        self._data = {} if data is None else data
        if row_names is not None and not isinstance(row_names, ut.StringList):
            row_names = ut.StringList(row_names)
        self._row_names = row_names
        self._number_of_rows = _guess_number_of_rows(
            number_of_rows,
            self._data,
            self._row_names,
        )

        if column_names is None:
            column_names = ut.StringList(self._data.keys())
        elif not isinstance(column_names, ut.StringList):
            column_names = ut.StringList(column_names)
        self._column_names = column_names

        self._metadata = {} if metadata is None else metadata
        self._mcols = mcols

        if validate:
            _validate_rows(self._number_of_rows, self._data, self._row_names)
            _validate_columns(self._column_names, self._data, self._mcols)

    def __repr__(self) -> str:
        output = "BiocFrame(data=" + ut.print_truncated_dict(self._data)
        output += ", number_of_rows=" + str(self.shape[0])

        if self._row_names:
            output += ", row_names=" + ut.print_truncated_list(self._row_names)
        output += ", column_names=" + ut.print_truncated_list(self._column_names)

        if self._mcols is not None and self._mcols.shape[1] > 0:
            # TODO: fix potential recursion here.
            output += ", mcols=" + repr(self._mcols)
        if len(self._metadata):
            output += ", metadata=" + ut.print_truncated_dict(self._metadata)

        output += ")"
        return output

    def __str__(self) -> str:
        output = f"BiocFrame with {self.dims[0]} row{'s' if self.shape[0] != 1 else ''}"
        output += f" and {self.dims[1]} column{'s' if self.dims[1] != 1 else ''}\n"

        nr = self.shape[0]
        added_table = False
        if nr and self.shape[1]:
            if nr <= 10:
                indices = range(nr)
                insert_ellipsis = False
            else:
                indices = [0, 1, 2, nr - 3, nr - 2, nr - 1]
                insert_ellipsis = True

            raw_floating = ut.create_floating_names(self._row_names, indices)
            if insert_ellipsis:
                raw_floating = raw_floating[:3] + [""] + raw_floating[3:]
            floating = ["", ""] + raw_floating

            columns = []
            for col in self._column_names:
                data = self._data[col]
                showed = ut.show_as_cell(data, indices)
                header = [col, "<" + ut.print_type(data) + ">"]
                showed = ut.truncate_strings(
                    showed, width=max(40, len(header[0]), len(header[1]))
                )
                if insert_ellipsis:
                    showed = showed[:3] + ["..."] + showed[3:]
                columns.append(header + showed)

            output += ut.print_wrapped_table(columns, floating_names=floating)
            added_table = True

        footer = []
        if self.mcols is not None and self.mcols.shape[1]:
            footer.append(
                "mcols("
                + str(self.mcols.shape[1])
                + "): "
                + ut.print_truncated_list(
                    self.mcols.column_names,
                    sep=" ",
                    include_brackets=False,
                    transform=lambda y: y,
                )
            )
        if len(self.metadata):
            footer.append(
                "metadata("
                + str(len(self.metadata))
                + "): "
                + ut.print_truncated_list(
                    list(self.metadata.keys()),
                    sep=" ",
                    include_brackets=False,
                    transform=lambda y: y,
                )
            )
        if len(footer):
            if added_table:
                output += "\n------\n"
            output += "\n".join(footer)

        return output

    def _define_output(self, in_place: bool = False) -> "BiocFrame":
        if in_place is True:
            return self
        else:
            return self.__copy__()

    @property
    def shape(self) -> Tuple[int, int]:
        """Dimensionality of the BiocFrame.

        Returns:
            Tuple[int, int]: A tuple (m, n),
            where `m` is the number of rows, and `n` is the number of columns.
        """
        return (self._number_of_rows, len(self._column_names))

    def get_row_names(self) -> Optional[ut.StringList]:
        """Row names of the BiocFrame.

        Returns:
            (List, optional): Row names if available, otherwise None.
        """
        return self._row_names

    def set_row_names(
        self, names: Optional[List], in_place: bool = False
    ) -> "BiocFrame":
        """Set new row names. All values in ``names`` must be unique.

        Args:
            names (List[str], optional): A list of unique values.
            in_place (bool): Whether to modify the ``BiocFrame`` object in place.

        Raises:
            ValueError: If the length of ``names`` does not match the number of rows.
            ValueError: If ``names`` is not unique.

        Returns:
            BiocFrame: A modified ``BiocFrame`` object, either as a copy of the original
            or as a reference to the (in-place-modified) original.
        """
        if names is not None:
            if len(names) != self.shape[0]:
                raise ValueError(
                    "Length of `names` does not match the number of rows, need to be "
                    f"{self.shape[0]} but provided {len(names)}."
                )
            if any(x is None for x in names):
                raise ValueError("`row_names` cannot contain None values.")
            if not isinstance(names, ut.StringList):
                names = ut.StringList(names)

        output = self._define_output(in_place)
        output._row_names = names
        return output

    @property
    def row_names(self) -> Optional[ut.StringList]:
        """Row names of the BiocFrame.

        Returns:
            (List, optional): Row names if available, otherwise None.
        """
        return self.get_row_names()

    @row_names.setter
    def row_names(self, names: Optional[List]):
        """Set new row names. All values in ``names`` must be unique. (in-place operation).

        Args:
            names (List[str], optional): A list of unique values.

        Raises:
            ValueError: If the length of ``names`` does not match the number of rows.
            ValueError: If ``names`` is not unique.
        """

        warn(
            "Setting property 'row_names' is an in-place operation, use 'set_row_names' instead",
            UserWarning,
        )

        self.set_row_names(names, in_place=True)

    @property
    def data(self) -> Dict[str, Any]:
        """Access columns as :py:class:`dict` Read-only property.

        Returns:
            Dict[str, Any]: Dictionary of columns and their values.
        """
        return self._data

    def get_column_names(self) -> ut.StringList:
        """Column names of the BiocFrame.

        Returns:
            List[str]: A list of column names.
        """
        return self._column_names

    def set_column_names(self, names: List[str], in_place: bool = False) -> "BiocFrame":
        """Set new column names. New names must be unique.

        Args:
            names (List[str]): A list of unique values.
            in_place (bool): Whether to modify the ``BiocFrame`` object in place.

        Raises:
            ValueError:
                If the length of ``names`` does not match the number of columns.
                If ``names`` is not unique.

        Returns:
            BiocFrame: A modified ``BiocFrame`` object, either as a copy of the original
            or as a reference to the (in-place-modified) original.
        """
        if len(names) != len(self._column_names):
            raise ValueError("Provided `names` does not match number of columns.")

        new_names = ut.StringList()
        new_data = {}
        for i, x in enumerate(names):
            if x is None:
                raise ValueError("Column names cannot contain None values.")
            y = str(x)
            if y in new_data:
                raise ValueError("Detected duplicate column name '" + y + "'.")
            new_names.append(y)
            new_data[y] = self._data[self.column_names[i]]

        output = self._define_output(in_place)
        output._column_names = new_names
        output._data = new_data
        return output

    @property
    def column_names(self) -> ut.StringList:
        """Column names of the BiocFrame.

        Returns:
            List[str]: A list of column names.
        """
        return self.get_column_names()

    @column_names.setter
    def column_names(self, names: List[str]):
        """Set new column names. New names must be unique (in-place operation).

        Args:
            names (List[str]): A list of unique values.

        Raises:
            ValueError:
                If the length of ``names`` does not match the number of columns.
                If ``names`` is not unique.
        """

        warn(
            "Setting property 'column_names' is an in-place operation, use 'set_column_names' instead",
            UserWarning,
        )

        self.set_column_names(names, in_place=True)

    def get_mcols(self) -> Union[None, "BiocFrame"]:
        """The ``mcols``, containing annotation on the columns."""
        return self._mcols

    def set_mcols(
        self, mcols: Union[None, "BiocFrame"], in_place: bool = False
    ) -> "BiocFrame":
        """Set new `mcols`, containing annotations on the columns.

        Args:
            mcols (Biocframe, optional): New mcols. Can be `None` to remove this information.
            in_place (bool): Whether to modify the ``BiocFrame`` object in place.

        Returns:
            BiocFrame: A modified ``BiocFrame`` object, either as a copy of the original
            or as a reference to the (in-place-modified) original.
        """
        if mcols is not None:
            if mcols.shape[0] != self.shape[1]:
                raise ValueError(
                    "Number of rows in `mcols` should be equal to the number of columns."
                )

        output = self._define_output(in_place)
        output._mcols = mcols
        return output

    @property
    def mcols(self) -> Union[None, "BiocFrame"]:
        """The ``mcols``, containing annotation on the columns."""
        return self.get_mcols()

    @mcols.setter
    def mcols(self, mcols: Union[None, "BiocFrame"]):
        """Set new mcols (in-place operation).

        Args:
            mcols (Union[None, BiocFrame]): New metadata about column to set.
        """
        warn(
            "Setting property 'mcols' is an in-place operation, use 'set_mcols' instead",
            UserWarning,
        )

        self.set_mcols(mcols, in_place=True)

    def get_metadata(self) -> dict:
        """Access metadata.

        Returns:
            dict: Metadata object.
        """
        return self._metadata

    def set_metadata(self, metadata: dict, in_place: bool = False) -> "BiocFrame":
        """Set new metadata.

        Args:
            metadata (dict): New metadata object.
            in_place (bool): Whether to modify the ``BiocFrame`` object in place.

        Returns:
            BiocFrame: A modified ``BiocFrame`` object, either as a copy of the original
            or as a reference to the (in-place-modified) original.
        """
        if not isinstance(metadata, dict):
            raise TypeError(
                f"`metadata` must be a dictionary, provided {type(metadata)}."
            )

        output = self._define_output(in_place)
        output._metadata = metadata
        return output

    @property
    def metadata(self) -> dict:
        """Access metadata.

        Returns:
            dict: Metadata object.
        """
        return self.get_metadata()

    @metadata.setter
    def metadata(self, metadata: dict):
        """Set new metadata (in-place operation).

        Args:
            metadata (dict): New metadata object.
        """
        warn(
            "Setting property 'metadata' is an in-place operation, use 'set_metadata' instead",
            UserWarning,
        )

        self.set_metadata(metadata, in_place=True)

    def has_column(self, name: str) -> bool:
        """Check whether the column exists in the BiocFrame.

        Args:
            name (str): Name to check.

        Returns:
            bool: True if the column exists, otherwise False.
        """
        return name in self.column_names

    def get_column(self, index_or_name: Union[str, int]) -> Any:
        """Access a column by index or column label.

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

    def column(self, index_or_name: Union[str, int]) -> Any:
        """Access a column by index or column label. Alias to :py:meth:`~biocframe.BiocFrame.BiocFrame.get_column`.

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

        warn(
            "Method 'column' is deprecated, use 'get_column' instead",
            DeprecationWarning,
        )

        return self.get_column(index_or_name)

    def get_row(self, index_or_name: Union[str, int]) -> dict:
        """Access a row by index or row name.Alias to :py:meth:`~biocframe.BiocFrame.BiocFrame.get_row`.

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

    def row(self, index_or_name: Union[str, int]) -> dict:
        """Access a row by index or row name.

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

        warn(
            "Method 'row' is deprecated, use 'get_row' instead",
            DeprecationWarning,
        )

        return self.get_row(index_or_name)

    def slice(
        self,
        row_indices_or_names: Optional[SlicerTypes] = None,
        column_indices_or_names: Optional[SlicerTypes] = None,
    ) -> Union["BiocFrame", dict, list]:
        """Slice ``BiocFrame`` by index or values.

        Args:
            row_indices_or_names (SlicerTypes, optional): Row indices (index positions)
                or row names (string) to slice.

                Object must contain :py:attr:`biocframe.BiocFrame.BiocFrame.row_names` to slice by names.
                Defaults to None.

            column_indices_or_names (SlicerTypes, optional): Column indices (index positions)
                or column names (string) to slice. Defaults to None.

        Returns:
            Union["BiocFrame", dict, list]:
                - If a single row is sliced, returns a :py:class:`dict`.
                - If a single column is sliced, returns the same type of the column.
                - For all other scenarios, returns the same type as the caller with the subsetted rows and columns.
        """
        new_data = {}
        new_row_names = self._row_names
        new_column_names = self._column_names
        is_row_scalar = False
        is_col_scalar = False

        # slice the columns and data
        if column_indices_or_names is not None:
            new_column_indices, is_col_scalar = ut.normalize_subscript(
                column_indices_or_names, len(new_column_names), new_column_names
            )
            new_column_names = ut.subset_sequence(new_column_names, new_column_indices)

        for col in new_column_names:
            new_data[col] = self._data[col]

        # slice the rows of the data
        new_number_of_rows = self.shape[0]
        if row_indices_or_names is not None:
            new_row_names = self.row_names
            new_row_indices, is_row_scalar = ut.normalize_subscript(
                row_indices_or_names, self.shape[0], new_row_names
            )

            new_number_of_rows = len(new_row_indices)
            for k, v in new_data.items():
                new_data[k] = ut.subset(v, new_row_indices)
            if new_row_names is not None:
                new_row_names = ut.subset_sequence(new_row_names, new_row_indices)

        if is_row_scalar is True:
            rdata = {}
            for col in new_column_names:
                rdata[col] = new_data[col][0]
            return rdata
        elif is_col_scalar is True:
            return new_data[new_column_names[0]]

        mcols = self._mcols
        if mcols is not None:
            if column_indices_or_names is not None:
                mcols = mcols.slice(new_column_indices, None)

        current_class_const = type(self)
        return current_class_const(
            data=new_data,
            number_of_rows=new_number_of_rows,
            row_names=new_row_names,
            column_names=new_column_names,
            metadata=self._metadata,
            mcols=mcols,
            validate=False,
        )

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
            - If a single column is sliced, returns returns the same type of the column.
            - For all other scenarios, returns the same type as the caller with the subsetted rows and columns.
        """

        # not an array, single str, slice by column
        if isinstance(args, str):
            return self.slice(None, args)

        if isinstance(args, int):
            return self.slice(args, None)

        # not an array, a slice
        if isinstance(args, slice):
            return self.slice(args, None)

        if isinstance(args, list):
            # column names if everything is a string
            if ut.is_list_of_type(args, str):
                return self.slice(None, args)
            elif ut.is_list_of_type(args, int):
                return self.slice(args, None)
            else:
                raise TypeError(
                    "Arguments not supported! Since slice is a list, must contain either list of column "
                    "names or indices."
                )

        # tuple
        if isinstance(args, tuple):
            if len(args) == 0:
                raise ValueError("Arguments must specify atleast a single slice!")

            if len(args) == 1:
                return self.slice(args[0], None)
            elif len(args) == 2:
                return self.slice(
                    args[0],
                    args[1],
                )
            else:
                raise ValueError(
                    "Number of slices more than 2. `BiocFrame` only supports 2-dimensional slicing."
                )

        raise TypeError("Provided slice arguments are not supported!")

    def __setitem__(self, args, value: Union[List, "BiocFrame"]):
        """Add or re-assign a value to a column (in-place operation).

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
            args (str): Name of the column.
            value (List): New value to set.

        Raises:
            ValueError: If the length of ``value`` does not match the number of rows.
        """
        warn(
            "This method perform an in-place operation, use 'set_column' instead",
            UserWarning,
        )

        if isinstance(args, tuple):
            rows, cols = args

            row_idx, scalar = ut.normalize_subscript(
                rows, self.shape[0], names=self._row_names
            )
            if scalar:
                raise TypeError("row indices should be a sequence or slice")

            col_idx, scalar = ut.normalize_subscript(
                cols, self.shape[1], names=self._column_names
            )
            if scalar:
                current = self._data[self._column_names[col_idx[0]]]
                for j, k in enumerate(row_idx):
                    current[k] = value[j]
            else:
                for i in col_idx:
                    nm = self._column_names[i]
                    current = self._data[nm]
                    replacement = value._data[nm]
                    for j, k in enumerate(row_idx):
                        current[k] = replacement[j]
        else:
            if len(value) != self.shape[0]:
                raise ValueError(
                    "Length of `value`, does not match the number of the rows,"
                    f"need to be {self.shape[0]} but provided {len(value)}."
                )

            if args not in self.column_names:
                self._column_names.append(args)

                if self._mcols is not None:
                    self._mcols = self._mcols.combine(BiocFrame({}, number_of_rows=1))

            self._data[args] = value

    def __delitem__(self, name: str):
        """Remove a column (in-place operation).

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
        warn(
            "This method perform an in-place operation, use 'remove_column' instead",
            UserWarning,
        )
        self.remove_column(name, in_place=True)

    def set_column(
        self, column: str, value: Any, in_place: bool = False
    ) -> "BiocFrame":
        """Modify an existing column or add a new column. This is a convenience wrapper around :py:attr:`~set_columns`.

        Args:
            args (str): Name of an existing or new column.

            value (Any): Value of the new column.

            in_place (bool): Whether to modify the object in place. Defaults to False.

        Raises:
            TypeError: If row indices are not a sequence or slice.
            ValueError: If length of `value` does not match the number of rows.

        Returns:
            BiocFrame: A modified ``BiocFrame`` object, either as a copy of the original
            or as a reference to the (in-place-modified) original.
        """
        return self.set_columns({column: value}, in_place=in_place)

    def set_columns(
        self, columns: dict[str, Any], in_place: bool = False
    ) -> "BiocFrame":
        """Modify existing columns or add new columns. This has the same effect as repeated calls to
        :py:attr:`~set_column` for multiple columns but is slightly more efficient when `in_place = False`.

        Args:
            args (str): Name of an existing or new column.

            columns (dict[str, Any]): Names and values of the new columns.

            in_place (bool): Whether to modify the object in place. Defaults to False.

        Raises:
            TypeError: If row indices are not a sequence or slice.
            ValueError: If length of `value` does not match the number of rows.

        Returns:
            BiocFrame: A modified ``BiocFrame`` object, either as a copy of the original
            or as a reference to the (in-place-modified) original.
        """
        output = self._define_output(in_place)
        if not in_place:
            output._data = copy(output._data)
        is_colnames_copied = False
        previous = len(output._column_names)

        for column, value in columns.items():
            if ut.get_height(value) != output.shape[0]:
                raise ValueError(
                    "Length of `value`, does not match the number of the rows,"
                    f"need to be {output.shape[0]} but provided {len(value)}."
                )

            if column not in output._column_names:
                if not in_place and not is_colnames_copied:
                    output._column_names = copy(output._column_names)
                    is_colnames_copied = True
                output._column_names.append(column)

            output._data[column] = value

        if output._mcols is not None:
            newly_added = len(output._column_names) - previous
            if newly_added:
                mcols = output._mcols._define_output(in_place)
                if not in_place:
                    mcols._data = copy(mcols._data)

                for mcol in mcols.get_column_names():
                    mcolumn = mcols.column(mcol)
                    if isinstance(mcolumn, numpy.ndarray):
                        if not numpy.ma.is_masked(mcolumn):
                            mcolumn = numpy.ma.array(mcolumn, mask=False)
                        mcolumn = numpy.ma.concatenate(
                            [
                                mcolumn,
                                numpy.ma.array(
                                    numpy.zeros(newly_added, dtype=mcolumn.dtype),
                                    mask=True,
                                ),
                            ]
                        )
                    else:
                        mcolumn = ut.combine_sequences(mcolumn, [None] * newly_added)
                    mcols._data[mcol] = mcolumn

                output._mcols = mcols

        return output

    def remove_column(self, column: str, in_place: bool = False) -> "BiocFrame":
        """Remove a column. This is a convenience wrapper around :py:attr:`~remove_columns`.

        Args:
            column (str): Name of the column to remove.
            in_place (bool): Whether to modify the object in place. Defaults to False.

        Raises:
            ValueError: If column does not exist.

        Returns:
            BiocFrame: A modified ``BiocFrame`` object, either as a copy of the original
            or as a reference to the (in-place-modified) original.
        """
        return self.remove_columns([column], in_place=in_place)

    def remove_columns(
        self, columns: Sequence[str], in_place: bool = False
    ) -> "BiocFrame":
        """Remove any number of existing columns.

        Args:
            columns (str): Names of the columns to remove.
            in_place (bool): Whether to modify the object in place. Defaults to False.

        Raises:
            ValueError: If column does not exist.

        Returns:
            BiocFrame: A modified ``BiocFrame`` object, either as a copy of the original
            or as a reference to the (in-place-modified) original.
        """
        output = self._define_output(in_place)
        if not in_place:
            output._data = copy(output._data)

        for name in columns:
            if name not in output._data:
                raise ValueError(f"Column '{name}' does not exist.")
            del output._data[name]

        killset = set(columns)
        keep = []
        for i, col in enumerate(output._column_names):
            if col not in killset:
                keep.append(i)

        output._column_names = ut.subset_sequence(output._column_names, keep)
        if output._mcols is not None:
            output._mcols = output._mcols[keep, :]

        return output

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

        _data_copy = OrderedDict()
        for col in self.column_names:
            _data_copy[col] = self.column(col)
            if isinstance(self.column(col), ut.Factor):
                _data_copy[col] = _data_copy[col].to_pandas()

        return DataFrame(
            data=_data_copy, index=self._row_names, columns=self._column_names
        )

    # TODO: very primitive implementation, needs very robust testing
    # TODO: implement in-place, view
    def __array_ufunc__(self, func, method, *inputs, **kwargs) -> "BiocFrame":
        """Interface with NumPy array methods.

        Note: This is a very primitive implementation and needs tests to support different types.

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
    def columns(self) -> ut.StringList:
        """Alias to :py:meth:`~biocframe.BiocFrame.BiocFrame.column_names`.

        Returns:
            list: List of column names.
        """
        return self.get_column_names()

    @property
    def index(self) -> Optional[ut.StringList]:
        """Alias to :py:meth:`~biocframe.BiocFrame.BiocFrame.row_names`.

        Returns:
            (list, optional): List of row names if available, otherwise None.
        """
        return self.get_row_names()

    # compatibility with R interfaces
    @property
    def rownames(self) -> Optional[ut.StringList]:
        """Alias to :py:meth:`~biocframe.BiocFrame.BiocFrame.row_names`.

        Returns:
            (list, optional): List of row names if available, otherwise None.
        """
        return self.get_row_names()

    @rownames.setter
    def rownames(self, names: list):
        """Alias to :py:meth:`~biocframe.BiocFrame.BiocFrame.row_names` (in-place operation).

        Args:
            names (list): New row names.
        """
        return self.set_row_names(names, in_place=True)

    @property
    def colnames(self) -> ut.StringList:
        """Alias to :py:meth:`~biocframe.BiocFrame.BiocFrame.column_names`.

        Returns:
            list: list of column names.
        """
        return self.get_column_names()

    @colnames.setter
    def colnames(self, names: ut.StringList):
        """Alias to :py:meth:`~biocframe.BiocFrame.BiocFrame.column_names` (in-place operation).

        Args:
            names (list): New column names.
        """
        self.set_column_names(names, in_place=True)

    @property
    def dims(self) -> Tuple[int, int]:
        """Alias to :py:meth:`~biocframe.BiocFrame.BiocFrame.shape`.

        Returns:
            Tuple[int, int]: A tuple  (m, n),
            where `m` is the number of rows, and `n` is the number of columns.
        """
        return self.shape

    def combine(self, *other):
        """Combine multiple BiocFrame objects by row.

        Note: Fills missing columns with an array of `None`s.

        Args:
            *other (BiocFrame): BiocFrame objects.

        Raises:
            TypeError: If all objects are not of type BiocFrame.

        Returns:
            The same type as caller with the combined data.
        """
        if not ut.is_list_of_type(other, BiocFrame):
            raise TypeError("All objects to combine must be BiocFrame objects.")

        all_objects = [self] + list(other)

        all_columns = [x.column_names for x in all_objects]
        all_unique_columns = list(
            set([item for sublist in all_columns for item in sublist])
        )

        all_row_names = (
            [""] * len(self) if self.row_names is None else self.row_names.copy()
        )
        all_num_rows = sum([len(x) for x in all_objects])
        all_data = self.data.copy()

        for ocol in all_unique_columns:
            if ocol not in all_data:
                all_data[ocol] = [None] * len(self)

        for obj in other:
            for ocol in all_unique_columns:
                _tcol = None
                if ocol not in obj.column_names:
                    _tcol = [None] * len(obj)
                else:
                    _tcol = obj.column(ocol)

                all_data[ocol] = ut.combine(all_data[ocol], _tcol)

            rnames = obj.row_names
            if rnames is None:
                rnames = [""] * len(obj)

            all_row_names.extend(rnames)

        if (
            all([x is None or len(x) == 0 for x in all_row_names])
            or len(all_row_names) == 0
        ):
            all_row_names = None

        combined_mcols = None
        if self.mcols is not None:
            combined_mcols = self.mcols
            if len(all_unique_columns) > len(self.mcols):
                combined_mcols = self.mcols.combine(
                    BiocFrame(
                        {}, number_of_rows=len(all_unique_columns) - len(self.mcols)
                    )
                )

        current_class_const = type(self)
        return current_class_const(
            all_data,
            number_of_rows=all_num_rows,
            row_names=all_row_names,
            column_names=all_unique_columns,
            metadata=self._metadata,
            mcols=combined_mcols,
        )

    def __deepcopy__(self, memo=None, _nil=[]):
        """Make a deep copy of the object.

        Raises:
            Exception: If a column cannot be copied.

        Returns:
            The same type as caller.
        """
        from copy import deepcopy

        _colnames_copy = deepcopy(self.column_names)
        _num_rows_copy = deepcopy(self._number_of_rows)
        _rownames_copy = deepcopy(self.row_names)
        _metadata_copy = deepcopy(self.metadata)
        _mcols_copy = deepcopy(self._mcols) if self._mcols is not None else None

        # copy dictionary first
        _data_copy = OrderedDict()
        for col in _colnames_copy:
            try:
                _data_copy[col] = deepcopy(self.column(col))
            except Exception as e:
                raise Exception(
                    f"Cannot `deepcopy` column '{col}', full error: {str(e)}"
                ) from e

        current_class_const = type(self)
        return current_class_const(
            _data_copy,
            number_of_rows=_num_rows_copy,
            row_names=_rownames_copy,
            column_names=_colnames_copy,
            metadata=_metadata_copy,
            mcols=_mcols_copy,
        )

    def __copy__(self):
        """Make a shallow copy of the object.

        Any modifications to the copied object may also affect the original.

        Returns:
            The same type as caller.
        """
        current_class_const = type(self)
        new_instance = current_class_const(
            self._data,
            number_of_rows=self._number_of_rows,
            row_names=self._row_names,
            column_names=self._column_names,
            metadata=self._metadata,
            mcols=self._mcols,
        )

        return new_instance

    def copy(self):
        """Alias to :py:meth:`~biocframe.BiocFrame.BiocFrame.__copy__`.

        Returns:
            The same type as caller.
        """
        return self.__copy__()


@ut.combine_rows.register(BiocFrame)
def _combine_rows_bframes(*x: BiocFrame):
    return x[0].combine(*x[1:])


@ut.combine_columns.register(BiocFrame)
def _combine_cols_bframes(*x: BiocFrame):
    raise NotImplementedError(
        "`combine_cols` is not implemented for `BiocFrame` objects."
    )


@ut.extract_row_names.register(BiocFrame)
def _rownames_bframe(x: BiocFrame):
    return x.get_row_names()


@ut.extract_column_names.register(BiocFrame)
def _colnames_bframe(x: BiocFrame):
    return x.get_column_names()


@ut.show_as_cell.register(BiocFrame)
def _show_as_cell_BiocFrame(x: BiocFrame, indices: Sequence[int]) -> List[str]:
    constructs = []
    for i in indices:
        constructs.append([])

    for k in x._column_names:
        col = ut.show_as_cell(x._data[k], indices)
        for i, v in enumerate(col):
            constructs[i].append(v)

    for i, x in enumerate(constructs):
        constructs[i] = ":".join(x)

    return constructs
