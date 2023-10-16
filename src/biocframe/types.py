from typing import List, Optional, Tuple, Union

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"

SlicerTypes = Union[List[int], List[bool], List[str], slice, int, str]
SlicerArgTypes = Union[List[str], Tuple[SlicerTypes, Optional[SlicerTypes]]]
