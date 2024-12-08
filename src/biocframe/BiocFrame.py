from collections import OrderedDict
from copy import copy
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple, Union
from warnings import warn

import biocutils as ut
import numpy

__author__ = "Jayaram Kancherla, Aaron Lun"
__copyright__ = "jkanche"
__license__ = "MIT"


############################


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
                "Length of `row_names` and `number_of_rows` do not match, " f"{len(row_names)} != {number_of_rows}"
            )
        if any(x is None for x in row_names):
            raise ValueError("`row_names` cannot contain None values.")


def _validate_columns(
    column_names: List[str],
    data: Dict[str, Any],
    column_data: Optional["BiocFrame"],
) -> Tuple[List[str], Dict[str, Any]]:
    if sorted(column_names) != sorted(data.keys()):
        raise ValueError("Mismatch between `column_names` and the keys of `data`.")

    if column_data is not None:
        if column_data.shape[0] != len(column_names):
            raise ValueError("Number of rows in `column_data` should be equal to the number of columns.")


############################


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
            iter_row_index = self._bframe.row_names[self._current_index] if self._bframe.row_names is not None else None

            iter_slice = self._bframe.row(self._current_index)
            self._current_index += 1
            return (iter_row_index, iter_slice)

        raise StopIteration


############################


class BiocFrame:
    """`BiocFrame` is an alternative to :class:`~pandas.DataFrame`, with support for nested and flexible column types.
    Inspired by the ``DFrame`` class from Bioconductor's **S4Vectors** package. Any object may be used as a column,
    provided it has:

    - Some concept of "height", as defined by :py:func:`~biocutils.get_height.get_height` from **BiocUtils**.
      This defaults to the length as defined by ``__len__``.
    - The ability to be sliced by integer indices, as implemented by :py:func:`~biocutils.subset.subset` from **BiocUtils**.
      This defaults to calling ``__getitem__``.
    - The ability to be combined with other objects, as implemented in :py:func:`~biocutils.combine.combine` from **BiocUtils**.
    - The ability to perform an assignment, as implemented in :py:func:`~biocutils.assign.assign` from **BiocUtils**.

    This allows ``BiocFrame`` to accept arbitrarily complex classes (such as nested ``BiocFrame`` instances) as columns.
    """

    def __init__(
        self,
        data: Optional[Dict[str, Any]] = None,
        number_of_rows: Optional[int] = None,
        row_names: Optional[List] = None,
        column_names: Optional[List[str]] = None,
        column_data: Optional["BiocFrame"] = None,
        metadata: Optional[dict] = None,
        validate: bool = True,
    ) -> None:
        """Initialize a ``BiocFrame`` object from columns.

        Args:
            data:
                Dictionary of column names as `keys` and their values. All
                columns must have the same length. Defaults to an empty
                dictionary.

            number_of_rows:
                Number of rows. If not specified, inferred from ``data``. This
                needs to be provided if ``data`` is empty and ``row_names`` are
                not present.

            row_names:
                Row names. This should not contain missing strings.

            column_names:
                Column names. If not provided, inferred from the ``data``.
                This may be in a different order than the keys of ``data``.
                This should not contain missing strings.

            column_data:
                Metadata about columns. Must have the same number of rows as
                the length of ``column_names``. Defaults to None.

            metadata:
                Additional metadata. Defaults to an empty dictionary.

            validate:
                Internal use only.
        """
        self._data = {} if data is None else data
        if row_names is not None and not isinstance(row_names, ut.Names):
            row_names = ut.Names(row_names)
        self._row_names = row_names
        self._number_of_rows = int(
            _guess_number_of_rows(
                number_of_rows,
                self._data,
                self._row_names,
            )
        )

        if column_names is None:
            column_names = ut.Names(self._data.keys())
        elif not isinstance(column_names, ut.Names):
            column_names = ut.Names(column_names)
        self._column_names = column_names

        self._metadata = {} if metadata is None else metadata
        self._column_data = column_data

        if validate:
            _validate_rows(self._number_of_rows, self._data, self._row_names)
            _validate_columns(self._column_names, self._data, self._column_data)

    def _define_output(self, in_place: bool = False) -> "BiocFrame":
        if in_place is True:
            return self
        else:
            return self.__copy__()

    #################################
    ######>> Shape and stuff <<######
    #################################

    @property
    def shape(self) -> Tuple[int, int]:
        """
        Returns:
            Tuple containing the number of rows and columns in this ``BiocFrame``.
        """
        return (self._number_of_rows, len(self._column_names))

    def __len__(self) -> int:
        """
        Returns:
            Number of rows.
        """
        return self.shape[0]

    def __iter__(self) -> BiocFrameIter:
        """Iterator over rows."""
        return BiocFrameIter(self)

    @property
    def dims(self) -> Tuple[int, int]:
        """Alias for :py:attr:`~shape`."""
        return self.shape

    ##########################
    ######>> Printing <<######
    ##########################

    def __repr__(self) -> str:
        """
        Returns:
            A string representation of this ``BiocFrame``.
        """
        output = "BiocFrame(data=" + ut.print_truncated_dict(self._data)
        output += ", number_of_rows=" + str(self.shape[0])

        if self._row_names:
            output += ", row_names=" + ut.print_truncated_list(self._row_names)
        output += ", column_names=" + ut.print_truncated_list(self._column_names)

        if self._column_data is not None and self._column_data.shape[1] > 0:
            # TODO: fix potential recursion here.
            output += ", column_data=" + repr(self._column_data)
        if len(self._metadata):
            output += ", metadata=" + ut.print_truncated_dict(self._metadata)

        output += ")"
        return output

    def __str__(self) -> str:
        """
        Returns:
            A pretty-printed string containing the contents of this ``BiocFrame``.
        """
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
                showed = ut.truncate_strings(showed, width=max(40, len(header[0]), len(header[1])))
                if insert_ellipsis:
                    showed = showed[:3] + ["..."] + showed[3:]
                columns.append(header + showed)

            output += ut.print_wrapped_table(columns, floating_names=floating)
            added_table = True

        footer = []
        if self.column_data is not None and self.column_data.shape[1]:
            footer.append(
                "column_data("
                + str(self.column_data.shape[1])
                + "): "
                + ut.print_truncated_list(
                    self.column_data.column_names,
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

    ###########################
    ######>> Row names <<######
    ###########################

    def get_row_names(self) -> Optional[ut.Names]:
        """
        Returns:
            List of row names, or None if no row names are available.
        """
        return self._row_names

    def set_row_names(self, names: Optional[List], in_place: bool = False) -> "BiocFrame":
        """
        Args:
            names:
                List of strings. This should have length equal to the
                number of rows in the current ``BiocFrame``.

            in_place:
                Whether to modify the ``BiocFrame`` object in place.

        Returns:
            A modified ``BiocFrame`` object, either as a copy of the original
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
            if not isinstance(names, ut.Names):
                names = ut.Names(names)

        output = self._define_output(in_place)
        output._row_names = names
        return output

    @property
    def row_names(self) -> Optional[ut.Names]:
        """Alias for :py:attr:`~get_row_names`."""
        return self.get_row_names()

    @row_names.setter
    def row_names(self, names: Optional[List]):
        """Alias for :py:attr:`~set_row_names` with ``in_place = True``.

        As this mutates the original object, a warning is raised.
        """
        warn(
            "Setting property 'row_names' is an in-place operation, use 'set_row_names' instead",
            UserWarning,
        )
        self.set_row_names(names, in_place=True)

    @property
    def rownames(self) -> Optional[ut.Names]:
        """Alias for :py:attr:`~get_row_names`, provided for back-compatibility."""
        return self.get_row_names()

    @rownames.setter
    def rownames(self, names: list):
        """Alias for :py:attr:`~set_row_names` with ``in_place = True``, provided for back-compaibility only.

        As this mutates the original object, a warning is raised.
        """
        return self.set_row_names(names, in_place=True)

    ######################
    ######>> Data <<######
    ######################

    def get_data(self) -> Dict[str, Any]:
        """
        Returns:
            Dictionary of columns and their values.
        """
        return self._data

    @property
    def data(self) -> Dict[str, Any]:
        """Alias for :py:attr:`~get_data`."""
        return self.get_data()

    ##############################
    ######>> Column names <<######
    ##############################

    def get_column_names(self) -> ut.Names:
        """
        Returns:
            A list of column names.
        """
        return self._column_names

    def set_column_names(self, names: List[str], in_place: bool = False) -> "BiocFrame":
        """
        Args:
            names:
                List of unique strings, of length equal to the number of
                columns in this ``BiocFrame``.

            in_place:
                Whether to modify the ``BiocFrame`` object in place.

        Returns:
            A modified ``BiocFrame`` object, either as a copy of the original
            or as a reference to the (in-place-modified) original.
        """
        if len(names) != len(self._column_names):
            raise ValueError("Provided `names` does not match number of columns.")

        new_names = ut.Names()
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
    def column_names(self) -> ut.Names:
        """Alias for :py:attr:`~get_column_names`."""
        return self.get_column_names()

    @column_names.setter
    def column_names(self, names: List[str]):
        """Alias for :py:attr:`~set_column_names` with ``in_place = True``.

        As this mutates the original object, a warning is raised.
        """
        warn(
            "Setting property 'column_names' is an in-place operation, use 'set_column_names' instead",
            UserWarning,
        )
        self.set_column_names(names, in_place=True)

    @property
    def colnames(self) -> ut.Names:
        """Alias for :py:attr:`~get_column_names`, provided for back-compatibility only."""
        return self.get_column_names()

    @colnames.setter
    def colnames(self, names: ut.Names):
        """Alias for :py:attr:`~set_column_names` with ``in_place = True``, provided for back-compatibility only.

        As this mutates the original object, a warning is raised.
        """
        self.set_column_names(names, in_place=True)

    ##########################
    ######>> Metadata <<######
    ##########################

    def get_column_data(self, with_names: bool = True) -> Union[None, "BiocFrame"]:
        """
        Args:
            with_names:
                Whether to set the column names of this ``BiocFrame`` as
                the row names of the column data ``BiocFrame``.

        Returns:
            The annotations for each column. This may be None if no annotation
            is present, or is a ``BiocFrame`` where each row corresponds to a
            column and contains that column's metadata.
        """
        output = self._column_data
        if with_names and output is not None:
            output = output.set_row_names(self._column_names)
        return output

    def set_column_data(self, column_data: Union[None, "BiocFrame"], in_place: bool = False) -> "BiocFrame":
        """
        Args:
            column_data:
                New column data. This should either be a ``BiocFrame`` with the
                numbero of rows equal to the number of columns in the current object,
                or None to remove existing column data.

            in_place:
                Whether to modify the ``BiocFrame`` object in place.

        Returns:
            A modified ``BiocFrame`` object, either as a copy of the original
            or as a reference to the (in-place-modified) original.
        """
        if column_data is not None:
            if column_data.shape[0] != self.shape[1]:
                raise ValueError("Number of rows in `column_data` should be equal to the number of columns.")

        output = self._define_output(in_place)
        output._column_data = column_data
        return output

    @property
    def column_data(self) -> Union[None, "BiocFrame"]:
        """Alias for :py:attr:`~get_column_data`."""
        return self.get_column_data()

    @column_data.setter
    def column_data(self, column_data: Union[None, "BiocFrame"]):
        """Alias for :py:attr:`~set_column_data` with ``in_place = True``.

        As this mutates the original object, a warning is raised.
        """
        warn(
            "Setting property 'column_data' is an in-place operation, use 'set_column_data' instead",
            UserWarning,
        )
        self.set_column_data(column_data, in_place=True)

    def get_metadata(self) -> dict:
        """
        Returns:
            Dictionary of metadata for this object.
        """
        return self._metadata

    def set_metadata(self, metadata: dict, in_place: bool = False) -> "BiocFrame":
        """
        Args:
            metadata:
                New metadata for this object.

            in_place:
                Whether to modify the ``BiocFrame`` object in place.

        Returns:
            A modified ``BiocFrame`` object, either as a copy of the original
            or as a reference to the (in-place-modified) original.
        """
        if not isinstance(metadata, dict):
            raise TypeError(f"`metadata` must be a dictionary, provided {type(metadata)}.")
        output = self._define_output(in_place)
        output._metadata = metadata
        return output

    @property
    def metadata(self) -> dict:
        """Alias for :py:attr:`~get_metadata`."""
        return self.get_metadata()

    @metadata.setter
    def metadata(self, metadata: dict):
        """Alias for :py:attr:`~set_metadata` with ``in_place = True``.

        As this mutates the original object, a warning is raised.
        """
        warn(
            "Setting property 'metadata' is an in-place operation, use 'set_metadata' instead",
            UserWarning,
        )
        self.set_metadata(metadata, in_place=True)

    ################################
    ######>> Single getters <<######
    ################################

    def has_column(self, name: str) -> bool:
        """
        Args:
            name: Name of the column.

        Returns:
            Whether a column with the specified ``name`` exists in this object.
        """
        return name in self.column_names

    def get_column(self, column: Union[str, int]) -> Any:
        """
        Args:
            column:
                Name of the column, which must exist in :py:attr:`~get_column_names`.

                Alternatively, the integer index of the column of interest.

        Returns:
            The contents of the specified column.
        """
        if isinstance(column, int):
            if column < 0:
                raise IndexError("Index cannot be negative.")

            if column > len(self._column_names):
                raise IndexError("Index greater than the number of columns.")

            return self._data[self._column_names[column]]
        elif isinstance(column, str):
            if column not in self._column_names:
                raise AttributeError(f"Column: {column} does not exist.")

            return self._data[column]

        raise TypeError(f"'column' must be a string or integer, provided '{type(column)}'.")

    def column(self, column: Union[str, int]) -> Any:
        """Alias for :py:meth:`~get_column`, provided for back-compatibility only."""
        warn(
            "Method 'column' is deprecated, use 'get_column' instead",
            DeprecationWarning,
        )
        return self.get_column(column)

    def get_row(self, row: Union[str, int]) -> dict:
        """
        Args:
            row:
                Integer index of the row to access.

                If row names are available (see :py:attr:`~get_row_names`), a
                string may be supplied instead. The first occurrence of the
                string in the row names is used.

        Returns:
            A dictionary where the keys are column names and the values are
            the contents of the columns at the specified ``row``.
        """
        if isinstance(row, str):
            if self._row_names is None:
                raise ValueError("No row names present to find row '" + row + "'.")
            row = self._row_names.index(row)
            if row < 0:
                raise ValueError("Could not find row '" + row + "'.")
        elif not isinstance(row, int):
            raise TypeError("`row` must be either an integer index or row name.")

        collected = {}
        for col in self._column_names:
            collected[col] = self._data[col][row]
        return collected

    def row(self, row: Union[str, int]) -> dict:
        """Alias for :py:attr:`~get_row`, provided for back-compatibility only."""
        warn(
            "Method 'row' is deprecated, use 'get_row' instead",
            DeprecationWarning,
        )
        return self.get_row(row)

    #########################
    ######>> Slicers <<######
    #########################

    def get_slice(
        self,
        rows: Union[str, int, bool, Sequence],
        columns: Union[str, int, bool, Sequence],
    ) -> "BiocFrame":
        """Slice ``BiocFrame`` along the rows and/or columns, based on their indices or names.

        Args:
            rows:
                Rows to be extracted. This may be an integer, boolean, string,
                or any sequence thereof, as supported by
                :py:meth:`~biocutils.normalize_subscript.normalize_subscript`.
                Scalars are treated as length-1 sequences.

                Strings may only be used if row names are available (see
                :py:attr:`~get_row_names`). The first occurrence of each string
                in the row names is used for extraction.

            columns:
                Columns to be extracted. This may be an integer, boolean,
                string, or any sequence thereof, as supported by
                :py:meth:`~biocutils.normalize_subscript.normalize_subscript`.
                Scalars are treated as length-1 sequences.

        Returns:
            A ``BiocFrame`` with the specified rows and columns.
        """
        new_column_names = self._column_names
        if not (isinstance(columns, slice) and columns == slice(None)):
            new_column_indices, _ = ut.normalize_subscript(columns, len(new_column_names), new_column_names)
            new_column_names = ut.subset_sequence(new_column_names, new_column_indices)

        new_data = {}
        for col in new_column_names:
            new_data[col] = self._data[col]

        new_row_names = self._row_names
        new_number_of_rows = self.shape[0]
        if not (isinstance(rows, slice) and rows == slice(None)):
            new_row_names = self.row_names
            new_row_indices, _ = ut.normalize_subscript(rows, self.shape[0], new_row_names)

            new_number_of_rows = len(new_row_indices)
            for k, v in new_data.items():
                new_data[k] = ut.subset(v, new_row_indices)
            if new_row_names is not None:
                new_row_names = ut.subset_sequence(new_row_names, new_row_indices)

        column_data = self._column_data
        if column_data is not None:
            if columns != slice(None):
                column_data = column_data.slice(new_column_indices, slice(None))

        current_class_const = type(self)
        return current_class_const(
            data=new_data,
            number_of_rows=new_number_of_rows,
            row_names=new_row_names,
            column_names=new_column_names,
            metadata=self._metadata,
            column_data=column_data,
            validate=False,
        )

    def slice(self, rows: Sequence, columns: Sequence) -> "BiocFrame":
        """Alias for :py:attr:`~__getitem__`, for back-compatibility."""
        if rows is None:
            rows = slice(None)
        if columns is None:
            columns = slice(None)
        return self.__getitem__((rows, columns))

    def __getitem__(self, args: Union[int, str, Sequence, tuple]) -> Union["BiocFrame", Any]:
        """Wrapper around :py:attr:`~get_column` and :py:attr:`~get_slice` to obtain a slice of a ``BiocFrame`` or any
        of its columns.

        Args:
            args:
                A sequence or a scalar integer or string, specifying the
                columns to retain based on their names or indices.

                Alternatively a tuple of length 1. The first entry specifies
                the rows to retain based on their names or indices.

                Alternatively a tuple of length 2. The first entry specifies
                the rows to retain, while the second entry specifies the
                columns to retain, based on their names or indices.

        Returns:
            If ``args`` is a scalar, the specified column is returned. This is
            achieved internally by calling :py:attr:`~get_column`.

            If ``args`` is a sequence, a new ``BiocFrame`` is returned
            containing only the specified columns. This is achieved by just
            calling :py:attr:`~get_slice` with no row slicing.

            If ``args`` is a tuple of length 1, a new ``BiocFrame`` is returned
            containing the specified rows. This is achieved by just calling
            :py:attr:`~get_slice` with no column slicing.

            If ``args`` is a tuple of length 2, a new ``BiocFrame`` is returned
            containing the specified rows and columns. This is achieved by just
            calling :py:attr:`~get_slice` with the specified arguments.
        """
        if isinstance(args, (str, int)):
            return self.get_column(args)

        if isinstance(args, tuple):
            if len(args) == 0:
                raise ValueError("At least one slicing argument must be provided.")

            if len(args) == 1:
                return self.get_slice(args[0], slice(None))
            elif len(args) == 2:
                return self.get_slice(args[0], args[1])
            else:
                raise ValueError("`BiocFrame` only supports 2-dimensional slicing.")

        return self.get_slice(slice(None), args)

    def __setitem__(self, args: Union[int, str, Sequence, tuple], value: "BiocFrame"):
        """Wrapper around :py:attr:`~set_column` and :py:attr:`~set_slice` to modify a slice of a ``BiocFrame`` or any
        of its columns. As this modified the original object in place, a warning is raise.

        If ``args`` is a string, it is assumed to be a column name and
        ``value`` is expected to be the column contents; these are passed onto
        :py:attr:`~set_column` with ``in_place = True``.

        If ``args`` is a tuple, it is assumed to contain row and column indices.
        ``value`` is expected to be a ``BiocFrame`` containing replacement values.
        These are passed to :py:attr:`~set_slice` with ``in_place = True``.
        """
        if isinstance(args, tuple):
            warn(
                "This method performs an in-place operation, use 'set_slice' instead",
                UserWarning,
            )
            self.set_slice(args[0], args[1], value, in_place=True)
        else:
            warn(
                "This method performs an in-place operation, use 'set_column' instead",
                UserWarning,
            )
            self.set_column(args, value, in_place=True)

    def set_slice(
        self,
        rows: Union[int, str, bool, Sequence],
        columns: Union[int, str, bool, Sequence],
        value: "BiocFrame",
        in_place: bool = True,
    ) -> "BiocFrame":
        """Replace a slice of the ``BiocFrame`` given the row and columns of the slice.

        Args:
            rows:
                Rows to be replaced. This may be any sequence of strings,
                integers, or booleans (or mixture thereof), as supported by
                :py:meth:`~biocutils.normalize_subscript.normalize_subscript`.
                Scalars are treated as length-1 sequences.

                Strings may only be used if row names are available (see
                :py:attr:`~get_row_names`). The first occurrence of each string
                in the row names is used for extraction.

            columns:
                Columns to be replaced. This may be any sequence of strings,
                integers, or booleans (or mixture thereof), as supported by
                :py:meth:`~biocutils.normalize_subscript.normalize_subscript`.
                Scalars are treated as length-1 sequences.

            value:
                A ``BiocFrame`` containing replacement values. Each row
                corresponds to a row in ``rows``, while each column corresponds
                to a column in ``columns``. Note that the replacement is based
                on position, so row and column names in ``value`` are ignored.

            in_place:
                Whether to modify the ``BiocFrame`` object in place.

        Returns:
            A modified ``BiocFrame`` object, either as a copy of the original
            or as a reference to the (in-place-modified) original.
        """
        output = self._define_output(in_place)
        if not in_place:
            output._data = copy(output._data)

        row_idx, _ = ut.normalize_subscript(rows, output.shape[0], names=output._row_names)

        col_idx, _ = ut.normalize_subscript(columns, output.shape[1], names=output._column_names)

        for i, x in enumerate(col_idx):
            nm = output._column_names[x]
            output._data[nm] = ut.assign(
                output._data[nm],
                row_idx,
                replacement=value._data[value._column_names[i]],
            )

        return output

    ##############################
    ######>> Item setters <<######
    ##############################

    def __delitem__(self, name: str):
        """Alias for :py:attr:`~remove_column` with ``in_place = True``.

        As this mutates the original object, a warning is raised.
        """
        warn(
            "This method perform an in-place operation, use 'remove_column' instead",
            UserWarning,
        )
        self.remove_column(name, in_place=True)

    def set_column(self, column: Union[int, str], value: Any, in_place: bool = False) -> "BiocFrame":
        """Modify an existing column or add a new column. This is a convenience wrapper around :py:attr:`~set_columns`.

        Args:
            column:
                Name of an existing or new column. Alternatively, an index
                specifying the position of an existing column.

            value:
                Value of the new column. This should have the same height
                as the number of rows in the current object.

            in_place:
                Whether to modify the object in place.

        Returns:
            A modified ``BiocFrame`` object, either as a copy of the original
            or as a reference to the (in-place-modified) original.
        """
        return self.set_columns({column: value}, in_place=in_place)

    def set_columns(self, columns: Dict[str, Any], in_place: bool = False) -> "BiocFrame":
        """Modify existing columns or add new columns.

        Args:
            columns:
                Contents of the columns to set. Keys may be strings containing
                new or existing column names, or integers containing the position
                of the column. Values should be the contents of each column.

            in_place:
                Whether to modify the object in place. Defaults to False.

        Returns:
            A modified ``BiocFrame`` object, either as a copy of the original
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

            if isinstance(column, int):
                column = output._column_names[column]
            elif column not in output._data:
                if not in_place and not is_colnames_copied:
                    output._column_names = copy(output._column_names)
                    is_colnames_copied = True
                output._column_names.append(column)

            output._data[column] = value

        if output._column_data is not None:
            newly_added = len(output._column_names) - previous
            if newly_added:
                extras = BiocFrame({}, number_of_rows=newly_added)
                output._column_data = relaxed_combine_rows(output._column_data, extras)

        return output

    def remove_column(self, column: Union[int, str], in_place: bool = False) -> "BiocFrame":
        """Remove a column. This is a convenience wrapper around :py:attr:`~remove_columns`.

        Args:
            column:
                Name or positional index of the column to remove.

            in_place:
                Whether to modify the object in place. Defaults to False.

        Returns:
            A modified ``BiocFrame`` object, either as a copy of the original
            or as a reference to the (in-place-modified) original.
        """
        return self.remove_columns([column], in_place=in_place)

    def remove_columns(self, columns: Sequence[Union[int, str]], in_place: bool = False) -> "BiocFrame":
        """Remove any number of existing columns.

        Args:
            columns:
                Names or indices of the columns to remove.

            in_place:
                Whether to modify the object in place. Defaults to False.

        Returns:
            BiocFrame: A modified ``BiocFrame`` object, either as a copy of the original
            or as a reference to the (in-place-modified) original.
        """
        output = self._define_output(in_place)
        if not in_place:
            output._data = copy(output._data)

        killset = set()
        for name in columns:
            if isinstance(name, int):
                name = output._column_names[name]
            if name not in output._data:
                raise ValueError(f"Column '{name}' does not exist.")
            del output._data[name]
            killset.add(name)

        keep = []
        for i, col in enumerate(output._column_names):
            if col not in killset:
                keep.append(i)

        output._column_names = ut.subset_sequence(output._column_names, keep)
        if output._column_data is not None:
            output._column_data = output._column_data[keep, :]

        return output

    #########################
    ######>> Copying <<######
    #########################

    def __deepcopy__(self, memo=None, _nil=[]):
        """
        Returns:
            A deep copy of the current ``BiocFrame``.
        """
        from copy import deepcopy

        _colnames_copy = deepcopy(self.column_names)
        _num_rows_copy = deepcopy(self._number_of_rows)
        _rownames_copy = deepcopy(self.row_names)
        _metadata_copy = deepcopy(self.metadata)
        _column_data_copy = deepcopy(self._column_data) if self._column_data is not None else None

        # copy dictionary first
        _data_copy = OrderedDict()
        for col in _colnames_copy:
            try:
                _data_copy[col] = deepcopy(self.column(col))
            except Exception as e:
                raise Exception(f"Cannot `deepcopy` column '{col}', full error: {str(e)}") from e

        current_class_const = type(self)
        return current_class_const(
            _data_copy,
            number_of_rows=_num_rows_copy,
            row_names=_rownames_copy,
            column_names=_colnames_copy,
            metadata=_metadata_copy,
            column_data=_column_data_copy,
        )

    def __copy__(self):
        """
        Returns:
            A shallow copy of the current ``BiocFrame``.
        """
        current_class_const = type(self)
        new_instance = current_class_const(
            self._data,
            number_of_rows=self._number_of_rows,
            row_names=self._row_names,
            column_names=self._column_names,
            metadata=self._metadata,
            column_data=self._column_data,
        )

        return new_instance

    def copy(self):
        """Alias for :py:meth:`~__copy__`."""
        return self.__copy__()

    ##########################
    ######>> split by <<######
    ##########################

    def split(self, column_name: str, only_indices: bool = False) -> Dict[str, Union["BiocFrame", List[int]]]:
        """Split the object by a column.

        Args:
            column_name:
                Name of the column to split by.

            only_indices:
                Whether to only return indices.
                Defaults to False

        Returns:
            A dictionary of biocframe objects, with names representing the
            group and the value the sliced frames.

            if ``only_indices`` is True, the values contain the row indices
            that map to the same group.
        """
        if column_name not in self._column_names:
            raise ValueError(f"'{column_name}' is not a valid column name.")

        _column = self.get_column(column_name)

        _grps = {}
        for i in range(len(self)):
            _key = _column[i]
            if _key not in _grps:
                _grps[_key] = []

            _grps[_key].append(i)

        if only_indices is True:
            return _grps

        _sliced_grps = {}
        for k, v in _grps.items():
            _sliced_grps[k] = self[v,]

        return _sliced_grps

    ################################
    ######>> pandas interop <<######
    ################################

    @property
    def index(self) -> Optional[ut.Names]:
        """Alias to :py:attr:`~get_row_names`, provided for compatibility with **pandas**."""
        return self.get_row_names()

    @property
    def columns(self) -> ut.Names:
        """Alias for :py:attr:`~get_column_names`, provided for compatibility with **pandas**."""
        return self.get_column_names()

    def to_pandas(self):
        """Convert the ``BiocFrame`` into a :py:class:`~pandas.DataFrame` object.

        Returns:
            A :py:class:`~pandas.DataFrame` object. Column names of the resulting
            dataframe may be different is the `BiocFrame` is nested.
        """
        from pandas import DataFrame

        if len(self.column_names) > 0:
            _data_copy = self.flatten(as_type="dict")
            return DataFrame(data=_data_copy, index=self._row_names)
        else:
            return DataFrame(data={}, index=range(self._number_of_rows))

    @classmethod
    def from_pandas(cls, input: "pandas.DataFrame") -> "BiocFrame":
        """Create a ``BiocFrame`` from a :py:class:`~pandas.DataFrame` object.

        Args:
            input:
                Input data.

        Returns:
            A ``BiocFrame`` object.
        """

        from pandas import DataFrame

        if not isinstance(input, DataFrame):
            raise TypeError("`data` is not a pandas `DataFrame` object.")

        rdata = input.to_dict("list")
        rindex = None

        if input.index is not None:
            rindex = input.index.to_list()

        return cls(data=rdata, row_names=rindex, column_names=input.columns.to_list())

    ################################
    ######>> polars interop <<######
    ################################

    @classmethod
    def from_polars(cls, input: "polars.DataFrame") -> "BiocFrame":
        """Create a ``BiocFrame`` from a :py:class:`~polars.DataFrame` object.

        Args:
            input:
                Input data.

        Returns:
            A ``BiocFrame`` object.
        """

        from polars import DataFrame

        if not isinstance(input, DataFrame):
            raise TypeError("`data` is not a polars `DataFrame` object.")

        rdata = input.to_dict(as_series=False)

        return cls(data=rdata)

    def to_polars(self):
        """Convert the ``BiocFrame`` into a :py:class:`~polars.DataFrame` object.

        Returns:
            A :py:class:`~polars.DataFrame` object. Column names of the resulting
            dataframe may be different is the `BiocFrame` is nested.
        """
        from polars import DataFrame

        if len(self.column_names) > 0:
            _data_copy = self.flatten(as_type="dict")
            return DataFrame(data=_data_copy)
        else:
            return DataFrame(data={})

    ###############################
    ######>> Miscellaneous <<######
    ###############################

    def flatten(self, as_type: Literal["dict", "biocframe"] = "dict", delim: str = ".") -> "BiocFrame":
        """Flatten a nested BiocFrame object.

        Args:
            as_type:
                Return type of the result. Either a :py:class:`~dict` or a
                :py:class:`~biocframe.BiocFrame.BiocFrame` object.

            delim:
                Delimiter to join nested column names. Defaults to `"."`.

        Returns:
            An object with the type specified by ``as_type`` argument.
            If ``as_type`` is `dict`, an additional column "rownames" is added if the object
            contains rownames.
        """

        if as_type not in ["dict", "biocframe"]:
            raise ValueError("'as_type' must be either 'dict' or 'biocframe'.")

        _data_copy = OrderedDict()
        for col in list(self.get_column_names()):
            _cold = self.column(col)
            if isinstance(_cold, BiocFrame):
                _res = _cold.flatten(as_type=as_type)
                for k in _res.keys():
                    _data_copy[f"{col}{delim}{k}"] = _res[k]
            elif isinstance(_cold, ut.Factor):
                _data_copy[col] = _cold.to_pandas()
            else:
                _data_copy[col] = _cold

        if as_type == "biocframe":
            return BiocFrame(_data_copy, row_names=self._row_names)

        if self._row_names is not None:
            _data_copy["rownames"] = self._row_names

        return _data_copy

    def combine(self, *other):
        """Wrapper around :py:func:`~relaxed_combine_rows`, provided for back-compatibility only."""
        return relaxed_combine_rows([self] + other)

    # TODO: very primitive implementation, needs very robust testing
    # TODO: implement in-place, view
    def __array_ufunc__(self, func, method, *inputs, **kwargs) -> "BiocFrame":
        """Interface for NumPy array methods.

        Note: This is a very primitive implementation and needs tests to support different types.

        Returns:
            An object with the same type as the caller.
        """

        warn("Not all NumPy array methods are fully tested.", UserWarning)

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


############################


@ut.combine_rows.register(BiocFrame)
def _combine_rows_bframes(*x: BiocFrame):
    if not ut.is_list_of_type(x, BiocFrame):
        raise TypeError("All objects to combine must be BiocFrame objects.")

    first = x[0]
    total_nrows = 0
    first_nc = first.shape[1]
    has_rownames = False
    for df in x:
        total_nrows += df.shape[0]
        if df._row_names is not None:
            has_rownames = True
        if df.shape[1] != first_nc:
            raise ValueError(
                "All objects to combine must have the same number of columns (expected "
                + str(first_nc)
                + ", got "
                + str(df.shape[1])
                + ")."
            )

    new_data = {}
    for i, col in enumerate(x[0]._column_names):
        current = []
        for df in x:
            if not df.has_column(col):
                raise ValueError(
                    "All objects to combine must have the same columns (missing '"
                    + col
                    + "' in object "
                    + str(i)
                    + ")."
                )
            current.append(df.column(col))
        new_data[col] = ut.combine(*current)

    new_rownames = None
    if has_rownames:
        new_rownames = []
        for df in x:
            other_names = df._row_names
            if other_names is None:
                other_names = [""] * df.shape[0]
            new_rownames += other_names

    current_class_const = type(first)
    return current_class_const(
        new_data,
        number_of_rows=total_nrows,
        row_names=new_rownames,
        column_names=first._column_names,
        metadata=first._metadata,
        column_data=first._column_data,
    )


@ut.combine_columns.register(BiocFrame)
def _combine_cols_bframes(*x: BiocFrame):
    if not ut.is_list_of_type(x, BiocFrame):
        raise TypeError("All objects to combine must be BiocFrame objects.")

    first = x[0]
    first_nr = first.shape[0]
    all_column_names = ut.Names()
    all_data = {}
    all_column_data = []
    for df in x:
        if df.shape[0] != first_nr:
            raise ValueError(
                "All objects to combine must have the same number of rows (expected "
                + str(first_nr)
                + ", got "
                + str(df.shape[0])
                + ")."
            )

        all_column_names += df._column_names
        all_column_data.append(df._column_data)
        for n in df._column_names:
            if n in all_data:
                raise ValueError("All objects to combine must have different columns (duplicated '" + n + "').")
            all_data[n] = df._data[n]

    combined_column_data = None
    if not all(y is None for y in all_column_data):
        for i, val in enumerate(all_column_data):
            if val is None:
                all_column_data[i] = BiocFrame({}, number_of_rows=x[i].shape[0])
        try:
            combined_column_data = ut.combine_rows(*all_column_data)
        except Exception as ex:
            raise ValueError("Failed to combine 'column_data' when combining 'BiocFrame' objects by column. " + str(ex))

    current_class_const = type(first)
    return current_class_const(
        all_data,
        number_of_rows=first_nr,
        row_names=first._row_names,
        column_names=all_column_names,
        metadata=first._metadata,
        column_data=combined_column_data,
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


@ut.assign_rows.register(BiocFrame)
def _assign_rows_BiocFrame(x: BiocFrame, indices: Sequence[int], replacement: BiocFrame) -> BiocFrame:
    return x.set_slice(indices, replacement.get_column_names(), replacement)


############################


# Could turn this into a generic, if it was more useful elsewhere.
def _construct_missing(col, n):
    if isinstance(col, numpy.ndarray):
        return numpy.ma.array(
            numpy.zeros(n, dtype=col.dtype),
            mask=True,
        )
    else:
        return [None] * n


@ut.relaxed_combine_rows.register(BiocFrame)
def relaxed_combine_rows(*x: BiocFrame) -> BiocFrame:
    """A relaxed version of the :py:func:`~biocutils.combine_rows.combine_rows` method for :py:class:`~BiocFrame`
    objects.  Whereas ``combine_rows`` expects that all objects have the same columns, ``relaxed_combine_rows`` allows
    for different columns. Absent columns in any object are filled in with appropriate placeholder values before
    combining.

    Args:
        x:
            One or more ``BiocFrame`` objects, possibly with differences in the
            number and identity of their columns.

    Returns:
        A ``BiocFrame`` that combines all ``x`` along their rows and contains
        the union of all columns. Columns absent in any ``x`` are filled in
        with placeholders consisting of Nones or masked NumPy values.
    """
    if not ut.is_list_of_type(x, BiocFrame):
        raise TypeError("All objects to combine must be BiocFrame objects.")

    new_colnames = []
    first_occurrence = {}
    for df in x:
        for col in df._column_names:
            if col not in first_occurrence:
                new_colnames.append(col)
                first_occurrence[col] = df._data[col]

    # Best attempt at creating a missing vector:
    edited = []
    for df in x:
        extras = {}
        for col in new_colnames:
            if not df.has_column(col):
                extras[col] = _construct_missing(
                    first_occurrence[col],
                    df.shape[0],
                )

        if len(extras):
            edited.append(df.set_columns(extras))
        else:
            edited.append(df)

    return ut.combine_rows(*edited)


############################


def _normalize_merge_key_to_index(x, i, by):
    if by is None:
        if x[i]._row_names is None:
            raise ValueError("Row names required as key but are absent in object " + str(i) + ".")
        return None
    elif isinstance(by, int):
        nc = x[i].shape[1]
        if by < -nc or by >= nc:
            raise ValueError("Integer 'by' is out of range for object " + str(i) + " (" + str(nc) + " columns).")
        if by < 0:
            return by + nc
        else:
            return by
    elif isinstance(by, str):
        ib = x[i]._column_names.map(by)
        if ib < 0:
            raise ValueError("No key column '" + by + "' in object " + str(i) + ".")
        return ib
    else:
        raise TypeError("Unknown type '" + type(by).__name__ + "' for the 'by' argument.")


def _get_merge_key(x, i, by):
    if by[i] is None:
        return x[i]._row_names
    else:
        return x[i].get_column(by[i])


def merge(
    x: Sequence[BiocFrame],
    by: Union[None, str, Sequence] = None,
    join: Literal["inner", "left", "right", "outer"] = "left",
    rename_duplicate_columns: bool = False,
) -> "BiocFrame":
    """Merge multiple :py:class:`~BiocFrame`` objects together by common columns or row names, yielding a combined
    object with a union of columns across all objects.

    Args:
        x:
            Sequence of ``BiocFrame`` objects. Each object may have any
            number and identity of rows and columns.

        by:
            If string, the name of column containing the keys. Each entry of
            ``x`` is assumed to have this column.

            If integer, the index of column containing the keys. The same
            index is used for each entry of ``x``.

            If None, keys are assumed to be present in the row names.

            Alternatively a sequence of strings, integers or None, specifying
            the location of the keys in each entry of ``x``.

        join:
            Strategy for the merge. For left and right joins, we consider the
            keys for the first and last object in ``x``, respectively.

        rename_duplicate_columns:
            Whether duplicated non-key columns across ``x`` should be
            automatically renamed in the merged object. If False, an error is
            raised instead.

    Returns:
        BiocFrame: A BiocFrame containing the merged contents.

        If ``by = None``, the keys are stored in the row names.

        If ``by`` is a string, keys are stored in the column of the same name.

        If ``by`` is a sequence, keys are stored in the row names if ``by[0] =
        None``, otherwise they are stored in the column named ``by[0]``.
    """
    if not ut.is_list_of_type(x, BiocFrame):
        raise TypeError("All objects to merge must be BiocFrame objects.")

    if by is None or isinstance(by, str) or isinstance(by, int):
        by = [_normalize_merge_key_to_index(x, i, by) for i in range(len(x))]
    else:
        if len(by) != len(x):
            raise ValueError("'by' list should have the same length as 'x'.")
        by = [_normalize_merge_key_to_index(x, i, b) for i, b in enumerate(by)]

    if join == "left":
        all_keys = _get_merge_key(x, 0, by)
    elif join == "right":
        all_keys = _get_merge_key(x, -1, by)
    elif join == "inner":
        tmp_keys = [_get_merge_key(x, i, by) for i in range(len(x))]
        all_keys = ut.intersect(*tmp_keys)
    elif join == "outer":
        tmp_keys = [_get_merge_key(x, i, by) for i in range(len(x))]
        all_keys = ut.union(*tmp_keys)
    else:
        raise ValueError("Unknown joining strategy '" + join + "'")

    new_data = {}
    new_columns = []
    raw_column_data = []
    for i, df in enumerate(x):
        noop = False
        if join == "left":
            noop = i == 0
        elif join == "right":
            noop = i == len(x) - 1

        if not noop:
            keep = ut.match(all_keys, _get_merge_key(x, i, by))
            has_missing = (keep < 0).sum()
            if has_missing:
                non_missing = len(keep) - has_missing
                reorg_keep = []
                reorg_permute = []
                for k in keep:
                    if k < 0:
                        reorg_permute.append(non_missing)
                    else:
                        reorg_permute.append(len(reorg_keep))
                        reorg_keep.append(k)

        survivor_columns = []
        for j, y in enumerate(df._column_names):
            on_key = by[i] == j
            if on_key and i > 0:  # skipping the key columns, except for the first.
                continue
            val = df._data[y]
            survivor_columns.append(j)

            if rename_duplicate_columns:
                original = y
                counter = 1
                while y in new_data:
                    counter += 1
                    y = original + " (" + str(counter) + ")"
            elif y in new_data:
                raise ValueError("Detected duplicate columns across objects to be merged ('" + y + "').")

            new_columns.append(y)
            if noop:
                new_data[y] = val
            elif on_key:
                new_data[y] = all_keys
            elif has_missing == 0:
                new_data[y] = ut.subset(val, keep)
            else:
                retained = ut.subset(val, reorg_keep)
                combined = ut.combine(retained, _construct_missing(val, 1))
                new_data[y] = ut.subset(combined, reorg_permute)

        if df._column_data is not None:
            raw_column_data.append(ut.subset_rows(df._column_data, survivor_columns))
        else:
            raw_column_data.append(len(survivor_columns))

    new_column_data = None
    if not all(isinstance(y, int) for y in raw_column_data):
        for i, val in enumerate(raw_column_data):
            if isinstance(val, int):
                raw_column_data[i] = BiocFrame({}, number_of_rows=val)
        new_column_data = relaxed_combine_rows(*raw_column_data)

    output = type(x[0])(
        new_data,
        column_names=new_columns,
        number_of_rows=ut.get_height(all_keys),
        column_data=new_column_data,
        metadata=x[0]._metadata,
    )

    if by[0] is None:
        output.set_row_names(all_keys, in_place=True)

    return output


############################


@ut.relaxed_combine_columns.register(BiocFrame)
def relaxed_combine_columns(*x: BiocFrame) -> BiocFrame:
    """Wrapper around :py:func:`~merge` that performs a left join on the row names."""
    return merge(x, join="left", by=None)
