from ..BiocFrame import BiocFrame

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def from_pandas(input: "pandas.DataFrame") -> BiocFrame:
    """Create a :py:class:`~biocframe.BiocFrame.BiocFrame` from a :py:class:`~pandas.DataFrame` object.

    Args:
        input:
            Input data.

    Returns:
        A :py:class:`~biocframe.BiocFrame.BiocFrame` object.
    """

    from pandas import DataFrame

    if not isinstance(input, DataFrame):
        raise TypeError("`data` is not a pandas `DataFrame` object.")

    rdata = input.to_dict("list")
    rindex = None

    if input.index is not None:
        rindex = input.index.to_list()

    return BiocFrame(data=rdata, row_names=rindex, column_names=input.columns.to_list())
