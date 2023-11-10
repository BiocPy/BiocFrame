from biocutils import combine_rows
import numpy


def relaxed_combine_rows(*x: "BiocFrame") -> "BiocFrame":
    """
    A relaxed version of the :py:meth:`~biocutils.combine_rows.combine_rows`
    generic that handles differences in the columns between objects.

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
                firstcol = first_occurrence[col]
                if isinstance(firstcol, numpy.ndarray):
                    ex = numpy.ma.array(numpy.zeros(df.shape[0], dtype=firstcol.dtype), mask=True)
                else:
                    ex = [None] * df.shape[0]
                extras[col] = ex

        if len(extras):
            edited.append(df.set_columns(extras))
        else:
            edited.append(df)
   
    # Now slapping everything together.
    return combine_rows(*edited)
