from copy import deepcopy
from typing import List, Sequence, Union

import biocutils as ut
from biocgenerics.combine import combine


class Factor:
    """Factor class, equivalent to R's ``factor``.

    This is a vector of integer codes, each of which is an index into a list of unique strings. The aim is to encode a
    list of strings as integers for easier numerical analysis.
    """

    def __init__(
        self,
        codes: Sequence[int],
        levels: Sequence[str],
        ordered: bool = False,
        validate: bool = True,
    ):
        """
        Args:
            codes:
                List of codes. Each value should be a non-negative
                integer that is less than the length of ``levels``.
                Entries may also be None.

            levels:
                List of levels containing unique strings.

            ordered:
                Whether the levels are ordered.

            validate:
                Whether to validate the arguments. Internal use only.
        """
        if not isinstance(codes, list):
            codes = list(codes)
        self._codes = codes  # could be more efficient with NumPy... but who cares.

        if not isinstance(levels, list):
            levels = list(levels)
        self._levels = levels

        self._ordered = ordered

        if validate:
            if not ut.is_list_of_type(self._codes, int, ignore_none=True):
                raise TypeError("all entries of 'codes' should be integers or None")
            if not ut.is_list_of_type(self._levels, str):
                raise TypeError("all entries of 'levels' should be non-missing strings")

            for x in codes:
                if x is None:
                    continue
                if x < 0 or x >= len(self._levels):
                    raise ValueError(
                        "all entries of 'codes' should refer to an entry of 'levels'"
                    )

            if len(set(self._levels)) < len(self._levels):
                raise ValueError("all entries of 'levels' should be unique")

    def get_codes(self) -> List[int]:
        """
        Returns:
            List of codes, used as indices into the levels from
            :py:attr:`~get_levels`. Values may also be None.
        """
        return self._codes

    def get_levels(self) -> List[str]:
        """
        Returns:
            List of unique factor levels.
        """
        return self._levels

    def get_ordered(self) -> bool:
        """
        Returns:
            Whether the levels are ordered.
        """
        return self._ordered

    def __len__(self) -> int:
        """
        Returns:
            Length of the factor in terms of the number of codes.
        """
        return len(self._codes)

    def __repr__(self) -> str:
        tmp = (
            "Factor(codes="
            + ut.print_truncated_list(self._codes)
            + ", levels="
            + ut.print_truncated_list(self._levels)
        )
        if self._ordered:
            tmp += ", ordered=True"
        tmp += ")"
        return tmp

    def __str__(self) -> str:
        message = (
            "Factor of length "
            + str(len(self._codes))
            + " with "
            + str(len(self._levels))
            + " level"
        )
        if len(self._levels) != 0:
            message += "s"
        message += "\n"

        message += (
            "values: "
            + ut.print_truncated_list(self._codes, transform=lambda i: self._levels[i])
            + "\n"
        )
        message += (
            "levels: "
            + ut.print_truncated_list(self._levels, transform=lambda x: x)
            + "\n"
        )
        message += "ordered: " + str(self._ordered)
        return message

    def __getitem__(self, args: Union[int, Sequence[int]]) -> Union[str, "Factor"]:
        """
        Args:
            args:
                Sequence of integers specifying the elements of interest.
                Alternatively an integer specifying a single element.

        Returns:
            If ``args`` is a sequence, a new ``Factor`` is returned containing
            only the elements of interest from ``args``.

            If ``args`` is an integer, a string is returned containing the
            level corresponding to the code at position ``args``.
        """
        args, scalar = ut.normalize_subscript(args, len(self), None)
        if scalar:
            x = self._codes[args[0]]
            if x is not None:
                return self._levels[x]
            else:
                return x

        new_codes = []
        for i in args:
            new_codes.append(self._codes[i])
        return Factor(new_codes, self._levels, self._ordered, validate=False)

    def __setitem__(self, args: Sequence[int], value: "Factor"):
        """
        Args:
            args: Sequence of integers specifying the elements to be replaced.

            value: A ``Factor`` containing the replacement values.

        Returns:
            The ``args`` elements in the current object are replaced with the
            corresponding values in ``value``. This is performed by finding the
            level for each entry of the replacement ``value``, matching it to a
            level in the current object, and replacing the entry of ``codes``
            with the code of the matched level. If there is no matching level,
            None is inserted instead.
        """
        if isinstance(args, slice):
            args = range(*args.indices(len(self._codes)))

        if self._levels == value._levels:
            for i, x in enumerate(args):
                self._codes[x] = value._codes[i]
        else:
            lmapping = {}
            for i, x in enumerate(self._levels):
                lmapping[x] = i
            mapping = []
            for x in value._levels:
                if x in lmapping:
                    mapping.append(lmapping[x])
                else:
                    mapping.append(None)
            for i, x in enumerate(args):
                self._codes[x] = mapping[value._codes[i]]

    def drop_unused_levels(self, in_place: bool = False) -> "Factor":
        """
        Args:
            in_place: Whether to perform this modification in-place.

        Returns:
            If ``in_place = False``, a new ``Factor`` object is returned
            where all unused levels have been removed.

            If ``in_place = True``, unused levels are removed from the
            current object; a reference to the current object is returned.
        """
        if in_place:
            new_codes = self._codes
        else:
            new_codes = [None] * len(self._codes)

        in_use = [False] * len(self._levels)
        for x in self._codes:
            if x is not None:
                in_use[x] = True

        new_levels = []
        reindex = []
        for i, x in enumerate(in_use):
            if x:
                reindex.append(len(new_levels))
                new_levels.append(self._levels[i])
            else:
                reindex.append(None)

        for i, x in enumerate(self._codes):
            new_codes[i] = reindex[x]

        if in_place:
            self._levels = new_levels
            return self
        else:
            return Factor(new_codes, new_levels, self._ordered, validate=False)

    def set_levels(
        self, levels: Union[str, List[str]], in_place: bool = False
    ) -> "Factor":
        """
        Args:
            levels:
                A list of replacement levels. These should be unique strings
                with no missing values.

                Alternatively a single string containing an existing level in
                this object. The new levels are defined as a permutation of the
                existing levels where the provided string is now the first
                level. The order of all other levels is preserved.

            in_place:
                Whether to perform this modification in-place.

        Returns:
            If ``in_place = False``, a new ``Factor`` object is returned where
            the levels have been replaced. This will automatically adjust the
            codes so that they still refer to the same level in the new
            ``levels``. If a code refers to a level that is not present in the
            new ``levels``, it is replaced with None.

            If ``in_place = True``, the levels are replaced in the current
            object, and a reference to the current object is returned.
        """
        lmapping = {}
        if isinstance(levels, str):
            new_levels = [levels]
            for x in self._levels:
                if x == levels:
                    lmapping[x] = 0
                else:
                    lmapping[x] = len(new_levels)
                    new_levels.append(x)
            if levels not in lmapping:
                raise ValueError(
                    "string 'levels' should already be present among object levels"
                )
        else:
            if not ut.is_list_of_type(levels, str):
                raise TypeError("all entries of 'levels' should be non-missing strings")
            new_levels = levels
            for i, x in enumerate(levels):
                if x in lmapping:
                    raise ValueError("levels should be unique")
                lmapping[x] = i

        mapping = [None] * len(self._levels)
        for i, x in enumerate(self._levels):
            if x in lmapping:
                mapping[i] = lmapping[x]

        new_codes = [None] * len(self._codes)
        for i, x in enumerate(self._codes):
            new_codes[i] = mapping[x]

        if in_place:
            self._codes = new_codes
            self._levels = new_levels
            return self
        else:
            return Factor(new_codes, new_levels, self._ordered, validate=False)

    def __copy__(self) -> "Factor":
        """
        Returns:
            A shallow copy of the ``Factor`` object.
        """
        return Factor(self._codes, self._levels, self._ordered, validate=False)

    def __deepcopy__(self, memo) -> "Factor":
        """
        Returns:
            A deep copy of the ``Factor`` object.
        """
        return Factor(
            deepcopy(self._codes, memo),
            deepcopy(self._levels, memo),
            self._ordered,
            validate=False,
        )

    def to_pandas(self):
        """Coerce to :py:class:`~pandas.Categorical` object.

        Returns:
            Categorical: A :py:class:`~pandas.Categorical` object.
        """
        from pandas import Categorical

        return Categorical(
            values=[self._levels[c] for c in self._codes],
            ordered=self._ordered,
        )

    @staticmethod
    def from_list(values: Sequence[str]) -> "Factor":
        """Represent a categorical vector as a Factor.

        Args:
            values (Sequence[str]): List of strings

        Raises:
            ValueError: If values is not a list.

        Returns:
            Factor: A Factor object.
        """
        levels, indices = ut.factor(values)

        return Factor(indices, levels=levels)


@combine.register(Factor)
def _combine_factors(*x: Factor):
    if not ut.is_list_of_type(x, Factor):
        raise ValueError("all elements to `combine` must be `Factor` objects")

    first = x[0]
    all_same = True
    for f in x[1:]:
        if f._levels != first._levels or f._ordered != first._ordered:
            all_same = False
            break

    if all_same:
        all_codes = []
        for f in x:
            all_codes.append(f._codes)
        new_codes = combine(*all_codes)
        new_levels = first._levels
        new_ordered = first._ordered
    else:
        all_levels_map = {}
        new_levels = []
        new_codes = []
        for f in x:
            mapping = []
            for i, y in enumerate(f._levels):
                if y not in all_levels_map:
                    all_levels_map[y] = len(new_levels)
                    new_levels.append(y)
                mapping.append(all_levels_map[y])
            for j in f._codes:
                if j is None:
                    new_codes.append(None)
                else:
                    new_codes.append(mapping[j])
        new_ordered = False

    return Factor(new_codes, new_levels, new_ordered, validate=False)
