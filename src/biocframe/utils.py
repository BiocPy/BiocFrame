from typing import Any, List, Union

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def _slice_or_index(data: Any, query: Union[slice, List[int]]):
    sliced_data = None
    if isinstance(query, range):
        _query_as_slice = slice(query.start, query.stop, query.step)
        sliced_data = data[_query_as_slice]
    elif isinstance(query, slice):
        sliced_data = data[query]
    elif isinstance(query, list):
        if not isinstance(data, list):
            try:
                return data[query]
            except Exception:
                pass

        sliced_data = [data[i] for i in query]
    else:
        raise TypeError("Cannot match column indices to a known operation!")

    return sliced_data
