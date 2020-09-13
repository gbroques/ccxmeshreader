# ccxmeshreader

[![PyPI version](https://badge.fury.io/py/ccxmeshreader.svg)](https://badge.fury.io/py/ccxmeshreader)
[![Conda version](https://anaconda.org/gbroques/ccxmeshreader/badges/version.svg)](https://anaconda.org/gbroques/ccxmeshreader)
[![Build Status](https://travis-ci.org/gbroques/ccxmeshreader.svg?branch=master)](https://travis-ci.org/gbroques/ccxmeshreader)

* [Introduction](#introduction)
* [Usage](#usage)
* [Supported Keywords](#supported-keywords)
    * [*NODE](#node)
    * [*ELEMENT](#element)
    * [*ELSET](#elset)
    * [*INCLUDE](#include)
* [Approach](#approach)
* [Limitations](#limitations)
* [Unit Tests](#unit-tests)

## Introduction
Reads a mesh from CalcluliX input (`.inp`) files.

Only supports a limited set of keywords defining the mesh. See [Supported Keywords](#supported-keywords) for details.

## Usage
```python
from ccxmeshreader import read_mesh


mesh = read_mesh('path/to/some.inp')
```

## Supported Keywords

### *NODE
Nodes and their coordinates are parsed and added to the dictionary returned by `read_mesh` in the `node_coordinates_by_number` key.

The `node_coordinates_by_number` key contains a dictionary where the key is the node number, and value is the coordinates as a three-element tuple with float values.

For example, given the following `*NODE` definition:
```
*NODE, NSET=Nall
1,  1.0, 0.0, 0.1
2,  3.0, 1.0, 2.0
3,  0.9, 5.0, 7.0
```
```python
mesh = read_mesh('example.inp')
print(mesh['node_coordinates_by_number'])
```
```
{
    1: (1.0, 0.0, 0.1),
    2: (3.0, 1.0, 2.0),
    3: (0.9, 5.0, 7.0)
}
```

Currently node sets are not supported, and the optional `NSET` parameter is ignored.

### *ELEMENT
Elements and their associated nodes are parsed and added to the dictionary returned by `read_mesh` in the `element_dict_by_type` key.

The `element_dict_by_type` key contains a dictionary where the key is the element type, and value is another dictionary where the key is the element number,
and value is a list of node numbers associated to the element.

For example, given the following `*ELEMENT` definition:
```
*ELEMENT, TYPE=C3D20R, ELSET=Eall
1,  1, 2, 3
2,  4, 5, 6
```
```python
mesh = read_mesh('example.inp')
print(mesh['element_dict_by_type'])
```
```
{
    'C3D20R': {
        1: [1, 2, 3]
        2: [4, 5, 6]
    }
}
```

Continuation of data-lines ending with a comma `,` is supported. For example:

```
*ELEMENT, TYPE=C3D20R, ELSET=Eall
1,  1, 2, 3,
    4, 5, 6
2,  7, 8, 9
```
```python
mesh = read_mesh('example.inp')
print(mesh['element_dict_by_type'])
```
```
{
    'C3D20R': {
        1: [1, 2, 3, 4, 5, 6]
        2: [7, 8, 9]
    }
}
```

---

If the `ELSET` parameter is provided, then the element set will be added to the `element_set_by_name` dictionary returned in the mesh of `read_mesh` with the corresponding element numbers.

For example, from the above `*ELEMENT` definition:
```python
mesh = read_mesh('example.inp')
print(mesh['element_set_by_name'])
```
```
{
    'Eall': {1, 2}
}
```

### *ELSET
Element set definitions are parsed and added to the dictionary returned by `read_mesh` in the `element_set_by_name` key.

The `element_set_by_name` key contains a dictionary where the key is the name of the element set, and value is a set of element numbers.

For example, given the following `*ELEMENT` and `*ELSET` definitions:
```
*ELEMENT, TYPE=S4, ELSET=E1
1, 1, 2, 3,
   4, 5, 6
2, 7, 8, 9

*ELSET, ELSET=E2, GENERATE
1, 4

*ELSET,ELSET=E3
E2, 5, 6
```
```python
mesh = read_mesh('example.inp')
print(mesh['element_set_by_name'])
```
```
{
    'E1': {1, 2},
    'E2': {1, 2, 3, 4}
    'E3': {1, 2, 3, 4, 5, 6}
}
```
The optional `GENERATE` parameter is respected with start, end, and step.

### *INCLUDE
Files specified by the `*INCLUDE` keyword are read, but currently limited to relative file paths, and assumed to be relative to the path passed to `read_mesh`.

Recursive includes (i.e. `*INCLUDE` statements in a previously included file) are not yet supported.

## Approach
The approach this library takes is to read the `.inp` file in a `while` loop, line-by-line, until there are no lines left, and collect the nodes and elements that make up the mesh into a dictionary.

It does not use an intermediate step of parsing the `.inp` file into an abstract syntax tree -- as doing so would be costly and likely involve a parsing library.

Thus, `ccxmeshreader` can be considered light-weight and performant.

## Limitations
Continuation of keyword lines is not supported.

For example, trying to read the following `.inp` file:

```
*ELEMENT, TYPE=C3D20R,
ELSET=Eall
```

raises a `ccxmeshreader.ParserError`.

## Unit Tests
Unit tests are included in the `tests/` directory, and can be ran with the following command:

    python -m unittest discover tests "*_test.py"
