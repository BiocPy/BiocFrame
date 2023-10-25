class Factor:
    def __init__(self, indices: Sequence[int], levels: List[str], ordered: bool = False, validate: bool = True):
        self._indices = list(indices) # could be more efficient with NumPy... but who cares.
        self._levels = list(levels)
        self._ordered = ordered

        if validate:
            for x in indices:
                if x is None:
                    continue
                if not isinstance(x, int):
                    raise TypeError("all entries of 'indices' should be integers")
                if x < 0 or x >= len(self._levels):
                    raise ValueError("all entries of 'indices' should refer to an entry of 'levels'")

    def indices(self):
        return self._indices

    def levels(self):
        return self._levels

    def ordered(self):
        return self._ordered

    def __len__(self):
        return len(self._indices)

    def __list__(self):
        output = [None] * len(self._indices)
        for i, x in enumerate(self._indices):
            if x is not None:
                output[i] = self._levels[x]
        return output 

    def __getitem__(self, args: Sequence[int]):
        new_indices = []
        for i in args:
            new_indices.append(self._indices[i])
        return Factor(new_indices, self._levels, self._ordered, validate=False)

    def __setitem__(self, args: Sequence[int], value: "Factor"):
        if self._levels == value._levels:
            for i, x in enumerate(args):
                self._indices[x] = value._indices[i]
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
                self._indices[i] = mapping[x]

    def drop_unused_levels(self, in_place: bool = False):
        new_indices = [None] * len(self._indices)
        new_levels = []
        level_map = {}
        for i, x in enumerate(self._indices):
            if x not in level_map:
                level_map[x] = len(new_levels)
                new_levels.append(x)
            new_indices[i] = level_map[x]

        if in_place:
            self._indices = new_indices
            self._levels = new_levels
            return self
        else:
            return Factor(new_indices, new_levels, self._ordered, validate=False)

    def set_levels(self, levels: List[str], in_place: bool = False):
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
                raise ValueError("string 'levels' should already be present among object levels")
        else:
            new_levels = levels
            for i, x in enumerate(levels):
                if x in lmapping:
                    raise ValueError("levels should be unique")
                lmapping[x] = i

        mapping = [None] * len(self._levels)
        for i, x in enumerate(self._levels):
            mapping[i] = lmapping[x]

        new_indices = [None] * self._indices
        for i, x in enumerate(self._indices):
            new_indices[i] = mapping[x]

        if in_place:
            self._indices = new_indices
            self._levels = new_levels
            return self
        else:
            return Factor(new_indices, new_levels, self._ordered, validate=False)

@combine.register(Factor)
def _combine_factors(*x: Factor):
    if not is_list_of_type(x, Factor):
        raise ValueError("all elements to `combine` must be `Factor` objects")

    first = x[0]
    all_same = True
    for f in x[1:]:
        if f._levels != first._levels or f._ordered != first._ordered:
            all_same = False
            break

    if all_same:
        all_indices = []
        for f in x:
            all_indices.append(f._indices)
        new_indices = combine(*all_indices)
        new_levels = first._levels
        new_ordered = first._ordered
    else:
        all_levels_map = {}
        new_levels = []
        new_indices = []
        for f in x:
            mapping = []
            for i, y in enumerate(f._levels):
                if y not in all_levels_map:
                    all_levels_map[y] = len(all_levels_seq)
                    new_levels.append(y)
                mapping.append(all_levels_map[y])
            for j in f._indices:
                new_indices.append(mapping[j])
        new_ordered = False

    return Factor(new_indices, new_levels, new_ordered, validate=False)
