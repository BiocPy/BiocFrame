from pandas import DataFrame

from ..BiocFrame import BiocFrame

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def from_pandas(input: DataFrame) -> BiocFrame:
    """Construct a new :py:class:`~biocframe.BiocFrame.BiocFrame` from
    :py:class:`~pandas.DataFrame` object.

    Args:
        input (DataFrame): Input data.

    Raises:
        TypeError: If ``input`` is not a :py:class:`~pandas.DataFrame`.

    Returns:
        BiocFrame: a new :py:class:`~biocframe.BiocFrame.BiocFrame` object.
    """

    if not isinstance(input, DataFrame):
        raise TypeError("data is not a pandas DataFrame object")

    rdata = input.to_dict("list")
    rindex = None

    if input.index is not None:
        rindex = input.index.to_list()

    return BiocFrame(data=rdata, rowNames=rindex, columnNames=input.columns.to_list())
