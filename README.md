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

# BiocFrame

This package provides `BiocFrame` class, an alternative to Pandas DataFrame's.

`BiocFrame` makes no assumption on the types of the columns, the minimum requirement is each column implements length: `__len__` and slice: `__getitem__` dunder methods. This allows `BiocFrame` to accept nested representations or any supported class as columns.


To get started, install the package from [PyPI](https://pypi.org/project/biocframe/)

```shell
pip install biocframe
```

## Usage

To construct a `BiocFrame` object, simply provide the data as a dictionary.

```python
from random import random
from biocframe import BiocFrame

obj = {
    "ensembl": ["ENS00001", "ENS00002", "ENS00003"],
    "symbol": ["MAP1A", "BIN1", "ESR1"],
}
bframe = BiocFrame(obj)
print(bframe)

## output

BiocFrame with 3 rows & 2 columns
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ ensembl <list> ┃ symbol <list> ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ ENS00001       │ MAP1A         │
│ ENS00002       │ BIN1          │
│ ENS00003       │ ESR1          │
└────────────────┴───────────────┘
```

You can specify complex representations as columns, for example

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

## output

   BiocFrame with 3 rows & 3 columns
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ row_names ┃ ensembl <list> ┃ symbol <list> ┃ ranges <BiocFrame>                          ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ row1      │ ENS00001       │ MAP1A         │ {'chr': 'chr1', 'start': 1000, 'end': 1100} │
│ row2      │ ENS00002       │ BIN1          │ {'chr': 'chr2', 'start': 1100, 'end': 4000} │
│ row3      │ ENS00002       │ ESR1          │ {'chr': 'chr3', 'start': 5000, 'end': 5500} │
└───────────┴────────────────┴───────────────┴─────────────────────────────────────────────┘
```

### Properties

Properties can be accessed directly from the object, for e.g. column names, row names and/or dimensions of the `BiocFrame`.

```python
# Dimensionality or shape
print(bframe.dims)

## output
(3, 2)

# get the column names
print(bframe.column_names)

## output
['ensembl', 'symbol']
```

#### Setters

To set various properties

```python
# set new column names
bframe.column_names = ["column1", "column2"]
print(bframe)

## output
BiocFrame with 3 rows & 2 columns
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ column1 <list> ┃ column2 <list> ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ ENS00001       │ MAP1A          │
│ ENS00002       │ BIN1           │
│ ENS00003       │ ESR1           │
└────────────────┴────────────────┘
```

To add new columns,

```python
bframe["score"] = range(2, 5)
bframe

## output
 BiocFrame with 3 rows & 3 columns
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ column1 <list> ┃ column2 <list> ┃ score <range> ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ ENS00001       │ MAP1A          │ 2             │
│ ENS00002       │ BIN1           │ 3             │
│ ENS00003       │ ESR1           │ 4             │
└────────────────┴────────────────┴───────────────┘
```

### Subset `BiocFrame`

Use the subset (`[]`) operator to **slice** the object,

```python
sliced = bframe[1:2, [True, False, False]]
print(sliced)

## output
BiocFrame with 1 row & 1 column
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ row_names ┃ column1 <list> ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━┩
│ 1         │ ENS00002       │
└───────────┴────────────────┘

```

This operation accepts different slice input types, you can either specify a boolean vector, a `slice` object, a list of indices, or row/column names to subset.


### Combine

`BiocFrame` implements the combine generic from [biocgenerics](https://github.com/BiocPy/generics). To combine multiple objects,

```python
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

from biocgenerics.combine import combine
combined = combine(bframe1, bframe2)

# OR an object oriented approach

combined = bframe.combine(bframe2)
```

For more details, check out the module reference [documentation](https://biocpy.github.io/BiocFrame/api/biocframe.html#biocframe.BiocFrame.BiocFrame).


<!-- pyscaffold-notes -->

## Note

This project has been set up using PyScaffold 4.5. For details and usage
information on PyScaffold see https://pyscaffold.org/.
