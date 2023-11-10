import biocutils as ut
import numpy


# Could turn this into a generic, if it was more useful elsewhere.
def _construct_missing(col, n):
    if isinstance(col, numpy.ndarray):
        return numpy.ma.array(
            numpy.zeros(n, dtype=col.dtype),
            mask=True,
        )
    else:
        return [None] * n


def relaxed_combine_rows(*x: "BiocFrame") -> "BiocFrame":
    """A relaxed version of the :py:meth:`~biocutils.combine_rows.combine_rows` method for ``BiocFrame`` objects.
    Whereas ``combine_rows`` expects that all objects have the same columns, ``relaxed_combine_rows`` allows for
    different columns. Absent columns in any object are filled in with appropriate placeholder values before combining.

    Args:
        x:
            One or more ``BiocFrame`` objects, possibly with differences in the
            number and identity of their columns.

    Returns:
        A ``BiocFrame`` that combines all ``x`` along their rows and contains
        the union of all columns. Columns absent in any ``x`` are filled in
        with placeholders consisting of Nones or masked NumPy values.
    """
    new_colnames = []
    first_occurrence = {}
    for df in x:
        for col in df._column_names:
            if col not in first_occurrence:
                new_colnames.append(col)
                first_occurrence[col] = df._data[col]

    # Best attempt at creating a missing vector:
    edited = []
    for df in x:
        extras = {}
        for col in new_colnames:
            if not df.has_column(col):
                extras[col] = _construct_missing(
                    first_occurrence[col],
                    df.shape[0],
                )

        if len(extras):
            edited.append(df.set_columns(extras))
        else:
            edited.append(df)

    # Now slapping everything together.
    return ut.combine_rows(*edited)
