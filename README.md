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

This package provides a data-frame representation similar to a pandas `DataFrame`, with
support for nested column types.


## Install

Package is published to [PyPI](https://pypi.org/project/biocframe/)

```shell
pip install biocframe
```

## Usage

Lets create a `BiocFrame` from a dictionary

```python
from random import random
from biocframe import BiocFrame

bframe = BiocFrame(
    data = {
        "seqnames": [
            "chr1",
            "chr2",
            "chr2",
            "chr2",
            "chr1",
            "chr1",
            "chr3",
            "chr3",
            "chr3",
            "chr3",
        ]
        * 20,
        "starts": range(100, 300),
        "ends": range(110, 310),
        "strand": ["-", "+", "+", "*", "*", "+", "+", "+", "-", "-"] * 20,
        "score": range(0, 200),
        "GC": [random() for _ in range(10)] * 20,
    }
)
```

### Access Properties

Accessor methods/properties are available to access column names, row names and dims.

```python
# find the dimensions
print(bframe.dims)

# get the column names
print(bframe.columnNames)
```

### Setters

Using the Pythonic way to set properties

```python
# set new column names
bframe.columnNames = [... new colnames ...]
print(bframe.columnNames)

# add or reassign columns

bframe["score"] = range(200, 400)
```

### Slice the `BiocFrame`

Currently slicing is only supported by indices or names (column names or row names). A future version may implement pandas query-like operations.

```python
sliced_bframe = bframe[3:7, 2:5]
```

For more use cases including subset, checkout the [documentation](https://biocpy.github.io/BiocFrame/)


<!-- pyscaffold-notes -->

## Note

This project has been set up using PyScaffold 4.5. For details and usage
information on PyScaffold see https://pyscaffold.org/.
