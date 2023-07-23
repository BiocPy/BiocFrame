from typing import Any

__author__ = "jkanche, keviny2"
__copyright__ = "jkanche"
__license__ = "MIT"


def is_list_of_type(x: Any, type: callable) -> bool:
    """Checks if `x` is a list of booleans.

    Args:
        x (Any): any object.
        type (callable): Type to check for, e.g. str, int

    Returns:
        bool: True if `x` is list and all values are of the same type.
    """
    return isinstance(x, list) and all(isinstance(item, type) for item in x)
