from ..BiocFrame import BiocFrame

try:
    from pandas import DataFrame
except ImportError:
    pass

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def from_pandas(input: "DataFrame") -> BiocFrame:
    """Read a :py:class:`~biocframe.BiocFrame.BiocFrame` from a :py:class:`~pandas.DataFrame` object.

    Args:
        input (:py:class:`~pandas.DataFrame`): Input data.

    Raises:
        TypeError: If ``input`` is not a :py:class:`~pandas.DataFrame`.

    Returns:
        BiocFrame: A :py:class:`~biocframe.BiocFrame.BiocFrame` object.
    """

    from pandas import DataFrame

    if not isinstance(input, DataFrame):
        raise TypeError("data is not a pandas `DataFrame` object.")

    rdata = input.to_dict("list")
    rindex = None

    if input.index is not None:
        rindex = input.index.to_list()

    return BiocFrame(data=rdata, row_names=rindex, column_names=input.columns.to_list())
