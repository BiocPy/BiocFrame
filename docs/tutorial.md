---
file_format: mystnb
kernelspec:
  name: python
---

# `BiocFrame` - Bioconductor-like data frames

`BiocFrame` class is a Bioconductor-friendly data frame class. Its primary advantage lies in not making assumptions about the types of the columns - as long as an object has a length (`__len__`) and supports slicing methods (`__getitem__`), it can be used inside a `BiocFrame`.

This flexibility allows us to accept arbitrarily complex objects as columns, which is often the case in Bioconductor objects. Also check out Bioconductor's [**S4Vectors**](https://bioconductor.org/packages/S4Vectors) package, which implements the `DFrame` class on which `BiocFrame` was based.

:::{.callout-note}
These classes follow a functional paradigm for accessing or setting properties, with further details discussed in [functional paradigm](https://biocpy.github.io/tutorial/chapters/philosophy.html) section.
:::

# Advantages of `BiocFrame`

One of the core principles guiding the implementation of the `BiocFrame` class is "**_what you put is what you get_**". Unlike Pandas `DataFrame`, `BiocFrame` makes no assumptions about the types of the columns provided as input. Some key differences to highlight the advantages of using `BiocFrame` are especially in terms of modifications to column types and handling nested dataframes.

## Inadvertent modification of types

As an example, Pandas `DataFrame` modifies the types of the input data. These assumptions may cause issues when interoperating between R and python.


```{code-cell}
import pandas as pd
import numpy as np
from array import array

df = pd.DataFrame({
    "numpy_vec": np.zeros(10),
    "list_vec": [1]* 10,
    "native_array_vec": array('d', [3.14] * 10) # less used but native python arrays
})

print("type of numpy_vector column:", type(df["numpy_vec"]), df["numpy_vec"].dtype)
print("type of list_vector column:", type(df["list_vec"]), df["list_vec"].dtype)
print("type of native_array_vector column:", type(df["native_array_vec"]), df["native_array_vec"].dtype)

print(df)
```

With `BiocFrame`, no assumptions are made, and the input data is not cast into (un)expected types:


```{code-cell}
from biocframe import BiocFrame
import numpy as np
from array import array

bframe_types = BiocFrame({
    "numpy_vec": np.zeros(10),
    "list_vec": [1]* 10,
    "native_array_vec": array('d', [3.14] * 10)
})

print("type of numpy_vector column:", type(bframe_types["numpy_vec"]))
print("type of list_vector column:", type(bframe_types["list_vec"]))
print("type of native_array_vector column:", type(bframe_types["native_array_vec"]))
print(bframe_types)
```

:::{.callout-note}
This behavior remains consistent when extracting, slicing, combining, or performing any supported operation on `BiocFrame` objects.
:::

## Handling complex nested frames

Pandas `DataFrame` does not support nested structures; therefore, running the snippet below will result in an error:

```python
df = pd.DataFrame({
    "ensembl": ["ENS00001", "ENS00002", "ENS00002"],
    "symbol": ["MAP1A", "BIN1", "ESR1"],
    "ranges": pd.DataFrame({
        "chr": ["chr1", "chr2", "chr3"],
        "start": [1000, 1100, 5000],
        "end": [1100, 4000, 5500]
    }),
})
print(df)
```

However, it is handled seamlessly with `BiocFrame`:


```{code-cell}
bframe_nested = BiocFrame({
    "ensembl": ["ENS00001", "ENS00002", "ENS00002"],
    "symbol": ["MAP1A", "BIN1", "ESR1"],
    "ranges": BiocFrame({
        "chr": ["chr1", "chr2", "chr3"],
        "start": [1000, 1100, 5000],
        "end": [1100, 4000, 5500]
    }),
})

print(bframe_nested)
```

:::{.callout-note}
This behavior remains consistent when extracting, slicing, combining, or performing any other supported operations on `BiocFrame` objects.
:::

# Construction

Creating a `BiocFrame` object is straightforward; just provide the `data` as a dictionary.


```{code-cell}
from biocframe import BiocFrame

obj = {
    "ensembl": ["ENS00001", "ENS00002", "ENS00003"],
    "symbol": ["MAP1A", "BIN1", "ESR1"],
}
bframe = BiocFrame(obj)
print(bframe)
```

::: {.callout-tip}
You can specify complex objects as columns, as long as they have some "length" equal to the number of rows.
For example, we can embed a `BiocFrame` within another `BiocFrame`.
:::


```{code-cell}
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
```

The `row_names` parameter is analogous to index in the pandas world and should not contain missing strings. Additionally, you may provide:

- `column_data`: A `BiocFrame`object containing metadata about the columns. This must have the same number of rows as the numbers of columns.
- `metadata`: Additional metadata about the object, usually a dictionary.
- `column_names`: If different from the keys in the `data`. If not provided, this is automatically extracted from the keys in the `data`.

# With other `DataFrame` libraries

# Pandas
`BiocFrame` is intended for accurate representation of Bioconductor objects for interoperability with R, many users may prefer working with **pandas** `DataFrame` objects for their actual analyses. This conversion is easily achieved:


```{code-cell}
from biocframe import BiocFrame
bframe3 = BiocFrame(
    {
        "foo": ["A", "B", "C", "D", "E"],
        "bar": [True, False, True, False, True]
    }
)

df = bframe3.to_pandas()
print(type(df))
print(df)
```

Converting back to a `BiocFrame` is similarly straightforward:


```{code-cell}
out = BiocFrame.from_pandas(df)
print(out)
```

## Polars

Similarly, you can easily go back and forth between `BiocFrame` and a polars `DataFrame`:

```{code-cell}
from biocframe import BiocFrame
bframe3 = BiocFrame(
    {
        "foo": ["A", "B", "C", "D", "E"],
        "bar": [True, False, True, False, True]
    }
)

pl = bframe3.to_polars()
print(pl)
```

# Extracting data

BiocPy classes follow a functional paradigm for accessing or setting properties, with further details discussed in [functional paradigm](https://biocpy.github.io/tutorial/chapters/philosophy.html#functional-discipline) section.

Properties can be directly accessed from the object:


```{code-cell}
print("shape:", bframe.shape)
print("column names (functional style):", bframe.get_column_names())
print("column names (as property):", bframe.column_names) # same as above
```

We can fetch individual columns:


```{code-cell}
print("functional style:", bframe.get_column("ensembl"))
print("w/ accessor", bframe["ensembl"])
```

And we can get individual rows as a dictionary:


```{code-cell}
bframe.get_row(2)
```

::: {.callout}
To retrieve a subset of the data in the `BiocFrame`, we use the subset (`[]`) operator.
This operator accepts different subsetting arguments, such as a boolean vector, a `slice` object, a sequence of indices, or row/column names.
:::


```{code-cell}
sliced_with_bools = bframe[1:2, [True, False, False]]
print("Subset using booleans: \n", sliced_with_bools)

sliced_with_names = bframe[[0,2], ["symbol", "ensembl"]]
print("\nSubset using column names: \n", sliced_with_names)

# Short-hand to get a single column:
print("\nShort-hand to get a single column: \n", bframe["ensembl"])
```

# Setting data

## Preferred approach

For setting properties, we encourage a **functional style** of programming to avoid mutating the object directly. This helps prevent inadvertent modifications of `BiocFrame` instances within larger data structures.



```{code-cell}
modified = bframe.set_column_names(["column1", "column2"])
print(modified)
```

Now let's check the column names of the original object,


```{code-cell}
# Original is unchanged:
print(bframe.get_column_names())
```

To add new columns, or replace existing ones:


```{code-cell}
modified = bframe.set_column("symbol", ["A", "B", "C"])
print(modified)

modified = bframe.set_column("new_col_name", range(2, 5))
print(modified)
```

Change the row or column names:


```{code-cell}
modified = bframe.\
    set_column_names(["FOO", "BAR"]).\
    set_row_names(['alpha', 'bravo', 'charlie'])
print(modified)
```

::: {.callout-tip}
The functional style allows you to chain multiple operations.
:::

We also support Bioconductor's metadata concepts, either along the columns or for the entire object:


```{code-cell}
modified = bframe.\
    set_metadata({ "author": "Jayaram Kancherla" }).\
    set_column_data(BiocFrame({"column_source": ["Ensembl", "HGNC" ]}))
print(modified)
```

## The not-preferred-way

Properties can also be set by direct assignment for in-place modification. We prefer not to do it this way as it can silently mutate ``BiocFrame`` instances inside other data structures.
Nonetheless:


```{code-cell}
testframe = BiocFrame({ "A": [1,2,3], "B": [4,5,6] })
testframe.column_names = ["column1", "column2" ]
print(testframe)
```

::: {.callout-caution}
Warnings are raised when properties are directly mutated. These assignments are the same as calling the corresponding `set_*()` methods with `in_place = True`.
It is best to do this only if the `BiocFrame` object is not being used anywhere else;
otherwise, it is safer to just create a (shallow) copy via the default `in_place = False`.
:::

Similarly, we could set or replace columns directly:


```{code-cell}
testframe["column2"] = ["A", "B", "C"]
testframe[1:3, ["column1","column2"]] = BiocFrame({"x":[4, 5], "y":["E", "F"]})
```

# Iterate over rows

You can iterate over the rows of a `BiocFrame` object. `name` is `None` if the object does not contain any `row_names`. To iterate over the first two rows:


```{code-cell}
for name, row in bframe[:2,]:
    print(name, row)
```

# Combining objects

`BiocFrame` implements methods for the various `combine` generics from [**BiocUtils**](https://github.com/BiocPy/biocutils). For example, to combine by row:



```{code-cell}
import biocutils

bframe1 = BiocFrame({
    "odd": [1, 3, 5, 7, 9],
    "even": [0, 2, 4, 6, 8],
})

bframe2 = BiocFrame({
    "odd": [11, 33, 55, 77, 99],
    "even": [0, 22, 44, 66, 88],
})

combined = biocutils.combine_rows(bframe1, bframe2)
print(combined)
```

Similarly, to combine by column:


```{code-cell}
bframe3 = BiocFrame({
    "foo": ["A", "B", "C", "D", "E"],
    "bar": [True, False, True, False, True]
})

combined = biocutils.combine_columns(bframe1, bframe3)
print(combined)
```

## Relaxed combine operation

By default, the combine methods assume that the number and identity of columns (for `combine_rows()`) or rows (for `combine_columns()`) are the same across objects. In situations where this is not the case, such as having different columns across objects, we can use `relaxed_combine_rows()` instead:


```{code-cell}
from biocframe import relaxed_combine_rows

modified2 = bframe2.set_column("foo", ["A", "B", "C", "D", "E"])

combined = biocutils.relaxed_combine_rows(bframe1, modified2)
print(combined)
```

## Sql-like join operation

Similarly, if the rows are different, we can use `BiocFrame`'s `merge` function. This function uses the *row_names* as the index to perform this operation; you can specify an alternative set of keys through the `by` parameter.


```{code-cell}
from biocframe import merge

modified1 = bframe1.set_row_names(["A", "B", "C", "D", "E"])
modified3 = bframe3.set_row_names(["C", "D", "E", "F", "G"])

combined = merge([modified1, modified3], by=None, join="outer")
print(combined)
```

# Empty Frames

We can create empty `BiocFrame` objects that only specify the number of rows. This is beneficial in scenarios where `BiocFrame` objects are incorporated into larger data structures but do not contain any data themselves.


```{code-cell}
empty = BiocFrame(number_of_rows=100)
print(empty)
```

Most operations detailed in this document can be performed on an empty `BiocFrame` object.


```{code-cell}
print("Column names:", empty.column_names)

subset_empty = empty[1:10,:]
print("\nSubsetting an empty BiocFrame: \n", subset_empty)
```

## Further reading

- Explore more details [the reference documentation](https://biocpy.github.io/BiocFrame/).
- Additionally, take a look at Bioconductor's [**S4Vectors**](https://bioconductor.org/packages/S4Vectors) package, which implements the `DFrame` class upon which `BiocFrame` was built.
