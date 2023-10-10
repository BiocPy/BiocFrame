from biocgenerics.combine import combine
from biocgenerics.combine_cols import combine_cols
from biocgenerics.combine_rows import combine_rows

from ._type_checks import is_list_of_type
from .BiocFrame import BiocFrame

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


@combine.register(BiocFrame)
def _combine_bframes(*x: BiocFrame):
    if not is_list_of_type(x, BiocFrame):
        raise ValueError("All elements to `combine` must be `BiocFrame` objects.")

    return x[0].combine(x[1:])


@combine_rows.register(BiocFrame)
def _combine_rows_bframes(*x: BiocFrame):
    if not is_list_of_type(x, BiocFrame):
        raise ValueError("All elements to `combine_rows` must be `BiocFrame` objects.")

    return x[0].combine(x[1:])


@combine_cols.register(BiocFrame)
def _combine_cols_bframes(*x: BiocFrame):
    if not is_list_of_type(x, BiocFrame):
        raise ValueError("All elements to `combine_cols` must be `BiocFrame` objects.")

    raise NotImplementedError(
        "`combine_cols` is not implemented for `BiocFrame` objects."
    )
