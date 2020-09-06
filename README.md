# ccxinpreader
Reads CalcluliX input (`.inp`) files.

## Usage
```python
from ccxinputreader import read_inp


result = read_inp('path/to/some.inp')
```

## Supported Keywords
Currently, only parsing the following keywords is supported:
* `*NODE`
* `*ELEMENT`
* `*ELSET`

## Limitations
Currently only supports parsing meshes, where a mesh consists of nodes connected by elements.

## Unit Tests
Unit tests are included in the `tests/` directory, and can be ran with the following command:

    python -m unittest discover tests "*_test.py"
