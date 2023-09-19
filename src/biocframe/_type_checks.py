"""Checks for types of objects."""

from collections.abc import Sequence as c_Sequence
from typing import Any, Sequence

__author__ = "jkanche, keviny2"
__copyright__ = "jkanche"
__license__ = "MIT"


def is_list_of_type(x: Sequence[Any], target_type: type) -> bool:
    """Checks if ``x`` is a list, and whether all elements of the list are of the same type.

    Args:
        x (Any): Any list-like object.
        target_type (callable): Type to check for, e.g. ``str``, ``int``.

    Returns:
        bool: True if ``x`` is :py:class:`list` and all elements are of the same type.
    """
    return (x, c_Sequence) and all(isinstance(item, target_type) for item in x)
