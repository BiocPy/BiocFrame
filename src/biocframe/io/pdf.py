import pandas as pd

from ..BiocFrame import BiocFrame

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"

def fromPandas(data: pd.DataFrame) -> BiocFrame:
    """Construct a new `BiocFrame` from pandas `DataFrame` object

    Args:
        data (pd.DataFrame): Pandas DataFrame object

    Raises:
        TypeError: if data is not a pandas `DataFrame`

    Returns:
        BiocFrame: a new `BiocFrame` object
    """

    if not isinstance(data, pd.DataFrame):
        raise TypeError("data is not a pandas DataFrame object")

    rdata = data.to_dict("list")
    rindex = None

    if data.index is not None:
        rindex = data.index.to_list()

    return BiocFrame(
        data=rdata, rowNames=rindex, columnNames=data.columns.to_list()
    )