# ccxinpreader
Reads CalcluliX input (`.inp`) files.

Currently only supports parsing meshes.

A mesh consists of nodes connected by elements.

Both nodes and elements may be grouped into sets.

## Usage
```python
from ccxinputreader import read_inp


result = read_inp('path/to/some.inp')
```

## Unit Tests
Unit tests are included in the `tests/` directory, and can be ran with the following command:

    python -m unittest discover tests "*_test.py"
