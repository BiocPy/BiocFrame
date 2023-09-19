"""Custom types for biocframe."""

from typing import Any, Dict, List, Protocol, Tuple, Union, runtime_checkable

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"

SimpleSlice = Union[slice, List[int]]
AtomicSlice = Union[int, bool, str]
RangeSlice = Union[
    List[AtomicSlice],
    slice,
    Tuple[Union[AtomicSlice, slice], Union[AtomicSlice, slice, None]],
]
AllSlice = Union[RangeSlice, AtomicSlice]


@runtime_checkable
class BiocSeq(Protocol):
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


ColType = Union[Dict[str, Any], List[Any], BiocSeq]
DataType = Union[
    Dict[str, ColType],
    Dict[str, Dict[str, Any]],
    Dict[str, List[Any]],
    Dict[str, BiocSeq],
]
