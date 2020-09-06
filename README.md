# ccxinpreader
Reads CalcluliX input (`.inp`) files.

Currently only supports parsing meshes.

A mesh consists of nodes connected by elements.

Both nodes and elements may be grouped into sets.

## Unit Tests
Unit tests are included in the `tests/` directory, and can be ran with the following command:

    python -m unittest discover tests "*_test.py"
