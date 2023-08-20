# Tutorial

To create a **BiocFrame** object, simply pass in the column representation as a dictionary.


```python
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

## Access Properties

Accessor methods/properties are available to access column names, row names and dims.

```python
# find the dimensions
print(bframe.dims)

# get the column names
print(bframe.columnNames)
```

## Setters

Using the Pythonic way to set properties

```python
# set new column names
bframe.columnNames = [... new colnames ...]
print(bframe.columnNames)

# add or reassign columns

bframe["score"] = range(200, 400)
```

## Slice the `BiocFrame`

Currently slicing is only supported by indices or names (column names or row names). A future version may implement pandas query-like operations.

```python
sliced_bframe = bframe[3:7, 2:5]
```
