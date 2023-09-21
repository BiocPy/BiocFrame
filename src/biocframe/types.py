"""Custom types for biocframe."""

from typing import (
    Any,
    List,
    Mapping,
    Protocol,
    Sequence,
    Tuple,
    Union,
    runtime_checkable,
)

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"

SimpleSlice = Union[slice, Sequence[int]]

AtomicSlice = Union[int, str]
SeqSlice = Sequence[Union[AtomicSlice, bool]]
TupleSlice = Tuple[
    Union[SeqSlice, slice],
    Union[SeqSlice, slice, None],
]
RangeSlice = Union[SeqSlice, slice, TupleSlice]
RowSlice = Tuple[AtomicSlice, "AllSlice"]
ColSlice = Tuple["AllSlice", AtomicSlice]
AllSlice = Union[RangeSlice, AtomicSlice, RowSlice, ColSlice]


@runtime_checkable
class BiocCol(Protocol):
    """The protocol for data types."""

    @property
    def shape(self) -> Sequence[int]:
        """Return the shape of the data."""
        ...

    def __getitem__(self, __key: Any) -> Any:
        """Slice the data."""
        ...

    def __len__(self) -> int:
        """Return the length of the data."""
        ...

    def __iter__(self) -> Any:
        """Iterate over the data."""
        ...


# Mapping is necessary as it is covariant which MutableMapping, etc. are not.
ColType = Union[Mapping[str, Any], Sequence[Any], BiocCol]
DataType = Union[
    Mapping[str, ColType],
    Mapping[str, Mapping[str, Any]],
    Mapping[str, Sequence[Any]],
    Mapping[str, BiocCol],
]
