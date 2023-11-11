# Changelog

## Version 0.5

- Bugfixes to avoid pass-by-reference effects when setting or removing columns.
- Provide functional-style method to add/remove multiple columns at once.
- Allow setting/removal of columns by position index instead of name.
- Provide a `relaxed_combine_rows` and `merge` function for flexible combining.
- Reduce the variety of arguments for `__getitem__`, to simplify user expectations.
- Internal refactoring to use generics from the BiocUtils package.

## Version 0.3
This release migrates the package to a more palatable Google's Python style guide. A major modification to the package is with casing, all `camelCase` methods, functions and parameters are now `snake_case`.

In addition, docstrings and documentation has been updated to use sphinx's features of linking objects to their types. Sphinx now also documents private and special dunder methods (e.g. `__getitem__`, `__copy__` etc). Intersphinx has been updated to link to references from dependent packages.

configuration for flake8, ruff and black has been added to pyproject.toml and setup.cfg to be less annoying.

In addition, pyscaffold has been updated to use "myst-parser" as the markdown compiler instead of recommonmark. As part of the pyscaffold setup, one may use pre-commits to run some of the routine tasks of linting and formatting before every commit. While this is sometimes annoying and can be ignored with `--no-verify`, it brings some consistency to the code base.

## Version 0.2
- refactor DataFrame as BiocFrame
- implementing slicing methods, tests

## Version 0.1

- Initial creation of DataFrame class
- Tests
- Documentation
- GitHub actions
