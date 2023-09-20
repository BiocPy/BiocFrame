"""Custom types for biocframe."""

from typing import (
    Any,
    Dict,
    List,
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
ListSlice = List[Union[AtomicSlice, bool]]
RangeSlice = Union[
    ListSlice,
    slice,
    Tuple[
        Union[ListSlice, slice],
        Union[ListSlice, slice, None],
    ],
]
RowSlice = Tuple[AtomicSlice, "AllSlice"]
ColSlice = Tuple["AllSlice", AtomicSlice]
AllSlice = Union[RangeSlice, AtomicSlice, RowSlice, ColSlice]


@runtime_checkable
class BiocCol(Protocol):
    """The protocol for data types."""

    @property
    def shape(self) -> List[int]:
        """Return the shape of the data."""
        ...

    def __getitem__(self, __key: Any) -> Any:
        """Slice the data."""
        ...

    def __len__(self) -> int:
        """Return the length of the data."""
        ...


ColType = Union[Dict[str, Any], List[Any], BiocCol]
DataType = Union[
    Dict[str, ColType],
    Dict[str, Dict[str, Any]],
    Dict[str, List[Any]],
    Dict[str, BiocCol],
]
