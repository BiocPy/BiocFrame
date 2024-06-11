<!-- These are examples of badges you might want to add to your README:
     please update the URLs accordingly

[![Built Status](https://api.cirrus-ci.com/github/<USER>/BiocFrame.svg?branch=main)](https://cirrus-ci.com/github/<USER>/BiocFrame)
[![ReadTheDocs](https://readthedocs.org/projects/BiocFrame/badge/?version=latest)](https://BiocFrame.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/BiocFrame/main.svg)](https://coveralls.io/r/<USER>/BiocFrame)
[![PyPI-Server](https://img.shields.io/pypi/v/BiocFrame.svg)](https://pypi.org/project/BiocFrame/)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/BiocFrame.svg)](https://anaconda.org/conda-forge/BiocFrame)
[![Monthly Downloads](https://pepy.tech/badge/BiocFrame/month)](https://pepy.tech/project/BiocFrame)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/BiocFrame)
-->

[![Project generated with PyScaffold](https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold)](https://pyscaffold.org/)
[![PyPI-Server](https://img.shields.io/pypi/v/BiocFrame.svg)](https://pypi.org/project/BiocFrame/)
![Unit tests](https://github.com/BiocPy/BiocFrame/actions/workflows/pypi-test.yml/badge.svg)

# Bioconductor-like data frames

## Overview

This package implements the `BiocFrame` class, a Bioconductor-friendly alternative to Pandas `DataFrame`.
The main advantage is that the `BiocFrame` makes no assumption on the types of the columns -
as long as an object has a length (`__len__`) and slicing methods (`__getitem__`), it can be used inside a `BiocFrame`.
This allows us to accept arbitrarily complex objects as columns, which is often the case in Bioconductor objects.

To get started, install the package from [PyPI](https://pypi.org/project/biocframe/):

```shell
pip install biocframe

# To install optional dependencies
pip install biocframe[optional]
```

## Construction

To construct a `BiocFrame` object, simply provide the data as a dictionary.

```python
from biocframe import BiocFrame

obj = {
    "ensembl": ["ENS00001", "ENS00002", "ENS00003"],
    "symbol": ["MAP1A", "BIN1", "ESR1"],
}
bframe = BiocFrame(obj)
print(bframe)
## BiocFrame with 3 rows and 2 columns
##      ensembl symbol
##       <list> <list>
## [0] ENS00001  MAP1A
## [1] ENS00002   BIN1
## [2] ENS00003   ESR1
```

You can specify complex objects as columns, as long as they have some "length" equal to the number of rows.
For example, we can nest a `BiocFrame` inside another `BiocFrame`:

```python
obj = {
    "ensembl": ["ENS00001", "ENS00002", "ENS00002"],
    "symbol": ["MAP1A", "BIN1", "ESR1"],
    "ranges": BiocFrame({
        "chr": ["chr1", "chr2", "chr3"],
        "start": [1000, 1100, 5000],
        "end": [1100, 4000, 5500]
    }),
}

bframe2 = BiocFrame(obj, row_names=["row1", "row2", "row3"])
print(bframe2)
## BiocFrame with 3 rows and 3 columns
##       ensembl symbol         ranges
##        <list> <list>    <BiocFrame>
## row1 ENS00001  MAP1A chr1:1000:1100
## row2 ENS00002   BIN1 chr2:1100:4000
## row3 ENS00002   ESR1 chr3:5000:5500
```

## Extracting data

Properties can be accessed directly from the object:

```python
print(bframe.shape)
## (3, 2)

print(bframe.get_column_names())
## ['ensembl', 'symbol']

print(bframe.column_names) # same as above
## ['ensembl', 'symbol']
```

We can fetch individual columns:

```python
bframe.get_column("ensembl")
## ['ENS00001', 'ENS00002', 'ENS00003']

bframe["ensembl"]
## ['ENS00001', 'ENS00002', 'ENS00003']
```

And we can get individual rows as a dictionary:

```python
bframe.get_row(2)
## {'ensembl': 'ENS00003', 'symbol': 'ESR1'}
```

To extract a subset of the data in the `BiocFrame`, we use the subset (`[]`) operator.
This accepts different subsetting arguments like a boolean vector, a `slice` object, a sequence of indices, or row/column names.

```python
sliced = bframe[1:2, [True, False, False]]
print(sliced)
## BiocFrame with 1 row and 1 column
##      column1
##       <list>
## [0] ENS00002

sliced = bframe[[0,2], ["symbol", "ensembl"]]
print(sliced)
## BiocFrame with 2 rows and 2 columns
##     symbol  ensembl
##     <list>   <list>
## [0]  MAP1A ENS00001
## [1]   ESR1 ENS00003

# Short-hand to get a single column:
bframe["ensembl"]
## ['ENS00001', 'ENS00002', 'ENS00003']
```

## Setting data

### Preferred approach

To set `BiocFrame` properties, we encourage a functional style of programming that avoids mutating the object.
This avoids inadvertent modification of `BiocFrame`s that are part of larger data structures.

```python
modified = bframe.set_column_names(["column1", "column2"])
print(modified)
## BiocFrame with 3 rows and 2 columns
##      column1 column2
##       <list>  <list>
## [0] ENS00001   MAP1A
## [1] ENS00002    BIN1
## [2] ENS00003    ESR1

# Original is unchanged:
print(bframe.get_column_names())
## ['ensembl', 'symbol']
```

To add new columns, or replace existing columns:

```python
modified = bframe.set_column("symbol", ["A", "B", "C"])
print(modified)
## BiocFrame with 3 rows and 2 columns
##      ensembl symbol
##       <list> <list>
## [0] ENS00001      A
## [1] ENS00002      B
## [2] ENS00003      C

modified = bframe.set_column("new_col_name", range(2, 5))
print(modified)
## BiocFrame with 3 rows and 3 columns
##      ensembl symbol new_col_name
##       <list> <list>      <range>
## [0] ENS00001  MAP1A            2
## [1] ENS00002   BIN1            3
## [2] ENS00003   ESR1            4
```

Change the row or column names:

```python
modified = bframe.\
    set_column_names(["FOO", "BAR"]).\
    set_row_names(['alpha', 'bravo', 'charlie'])
print(modified)
## BiocFrame with 3 rows and 2 columns
##              FOO    BAR
##           <list> <list>
##   alpha ENS00001  MAP1A
##   bravo ENS00002   BIN1
## charlie ENS00003   ESR1
```

We also support Bioconductor's metadata concepts, either along the columns or for the entire object:

```python
modified = bframe.\
    set_metadata({ "author": "Jayaram Kancherla" }).\
    set_column_data(BiocFrame({"column_source": ["Ensembl", "HGNC" ]}))
print(modified)
## BiocFrame with 3 rows and 2 columns
##      ensembl symbol
##       <list> <list>
## [0] ENS00001  MAP1A
## [1] ENS00002   BIN1
## [2] ENS00003   ESR1
## ------
## column_data(1): column_source
## metadata(1): author
```

### The other way

Properties can also be set by direct assignment for in-place modification.
We prefer not to do it this way as it can silently mutate ``BiocFrame`` instances inside other data structures.
Nonetheless:

```python
testframe = BiocFrame({ "A": [1,2,3], "B": [4,5,6] })
testframe.column_names = ["column1", "column2" ]
print(testframe)
## BiocFrame with 3 rows and 2 columns
##     column1 column2
##      <list>  <list>
## [0]       1       4
## [1]       2       5
## [2]       3       6
```

Similarly, we could set or replace columns directly:

```python
testframe["column2"] = ["A", "B", "C"]
testframe[1:3, ["column1","column2"]] = BiocFrame({"x":[4, 5], "y":["E", "F"]})
## BiocFrame with 3 rows and 2 columns
##     column1 column2
##      <list>  <list>
## [0]       1       A
## [1]       4       E
## [2]       5       F
```

These assignments are the same as calling the corresponding `set_*()` methods with `in_place = True`.
It is best to do this only if the `BiocFrame` object is not being used anywhere else;
otherwise, it is safer to just create a (shallow) copy via the default `in_place = False`.

## Combining objects

**BiocFrame** implements methods for the various `combine` generics from [**BiocUtils**](https://github.com/BiocPy/biocutils).
So, for example, to combine by row:

```python
import biocutils

bframe1 = BiocFrame(
    {
        "odd": [1, 3, 5, 7, 9],
        "even": [0, 2, 4, 6, 8],
    }
)

bframe2 = BiocFrame(
    {
        "odd": [11, 33, 55, 77, 99],
        "even": [0, 22, 44, 66, 88],
    }
)

combined = biocutils.combine_rows(bframe1, bframe2)
print(combined)
## BiocFrame with 10 rows and 2 columns
##        odd   even
##     <list> <list>
## [0]      1      0
## [1]      3      2
## [2]      5      4
## [3]      7      6
## [4]      9      8
## [5]     11      0
## [6]     33     22
## [7]     55     44
## [8]     77     66
## [9]     99     88
```

Similarly, to combine by column:

```python
bframe3 = BiocFrame(
    {
        "foo": ["A", "B", "C", "D", "E"],
        "bar": [True, False, True, False, True]
    }
)

combined = biocutils.combine_columns(bframe1, bframe3)
print(combined)
BiocFrame with 5 rows and 4 columns
       odd   even    foo    bar
    <list> <list> <list> <list>
[0]      1      0      A   True
[1]      3      2      B  False
[2]      5      4      C   True
[3]      7      6      D  False
[4]      9      8      E   True
```

By default, both methods above assume that the number and identity of columns (for `combine_rows()`) or rows (for `combine_columns()`) are the same across objects.
If this is not the case, e.g., with different columns across objects, we can use **BiocFrame**'s `relaxed_combine_rows()` instead:

```python
from biocframe import relaxed_combine_rows
modified2 = bframe2.set_column("foo", ["A", "B", "C", "D", "E"])
combined = relaxed_combine_rows(bframe1, modified2)
print(combined)
## BiocFrame with 10 rows and 3 columns
##        odd   even    foo
##     <list> <list> <list>
## [0]      1      0   None
## [1]      3      2   None
## [2]      5      4   None
## [3]      7      6   None
## [4]      9      8   None
## [5]     11      0      A
## [6]     33     22      B
## [7]     55     44      C
## [8]     77     66      D
## [9]     99     88      E
```

Similarly, if the rows are different, we can use **BiocFrame**'s `merge` function:

```python
from biocframe import merge
modified1 = bframe1.set_row_names(["A", "B", "C", "D", "E"])
modified3 = bframe3.set_row_names(["C", "D", "E", "F", "G"])
combined = merge([modified1, modified3], by=None, join="outer")
## BiocFrame with 7 rows and 4 columns
##      odd   even    foo    bar
##   <list> <list> <list> <list>
## A      1      0   None   None
## B      3      2   None   None
## C      5      4      A   True
## D      7      6      B  False
## E      9      8      C   True
## F   None   None      D  False
## G   None   None      E   True
```

## Playing nice with pandas

`BiocFrame` is intended for accurate representation of Bioconductor objects for interoperability with R.
Most users will probably prefer to work with **pandas** `DataFrame` objects for their actual analyses.
This conversion is easily achieved:

```python
from biocframe import BiocFrame
bframe = BiocFrame(
    {
        "foo": ["A", "B", "C", "D", "E"],
        "bar": [True, False, True, False, True]
    }
)

pd = bframe.to_pandas()
print(pd)
##   foo    bar
## 0   A   True
## 1   B  False
## 2   C   True
## 3   D  False
## 4   E   True
```

Conversion back to a ``BiocFrame`` is similarly easy:

```python
out = BiocFrame.from_pandas(pd)
print(out)
## BiocFrame with 5 rows and 2 columns
##      foo    bar
##   <list> <list>
## 0      A   True
## 1      B  False
## 2      C   True
## 3      D  False
## 4      E   True
```

## Further reading

Check out [the reference documentation](https://biocpy.github.io/BiocFrame/) for more details.

Also see check out Bioconductor's [**S4Vectors**](https://bioconductor.org/packages/S4Vectors) package,
which implements the `DFrame` class on which `BiocFrame` was based.
