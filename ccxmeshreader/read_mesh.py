import os
from collections import defaultdict
from typing import Callable, Dict, List, Set, Tuple

from .parser_error import ParserError

try:
    from typing import TypedDict  # >=3.8
    MeshType = TypedDict
except ImportError:
    from typing import NamedTuple  # <=3.7
    MeshType = NamedTuple


class Mesh(MeshType):
    node_coordinates_by_number: Dict[int, Tuple[float, float, float]]
    element_dict_by_type: Dict[str, Dict[int, List[int]]]
    element_set_by_name: Dict[str, Set[int]]


def read_mesh(path: str) -> Mesh:
    """Reads a CalculiX input file.

    Nodes are returned in a dictionary under the node_coordinates_by_number key,
    where the key is the node number,
    and value is the coordinates as a three-element tuple.

    Elements are returned in a dictionary under the element_dict_by_type key,
    where the key is the element type.
    The value is a dictionary where the key is element numbers,
    and value is a list of node numbers associated to the element.

    Element sets are returned in a dictionary under the element_set_by_name key,
    where the key is the name of the element set,
    and value is a set of element numbers.

    :param path: Path to CalculiX input file.
    :return: a dictionary with nodes, elements, and element sets.
    """
    result = {
        'node_coordinates_by_number': {},
        'element_dict_by_type': defaultdict(dict),
        'element_set_by_name': defaultdict(set)
    }
    with open(path, 'r') as f:
        line_num = 1

        # mutable variables
        data_type_to_read = ''
        previous_element_number = None
        element_type = ''
        element_set = ''
        generate_element = False
        include_file = None
        prev_line_num = None

        line = True
        while line:
            if include_file:
                line = include_file.readline()
                if line == '':
                    include_file.close()
                    include_file = None
                    line_num = prev_line_num + 1
                    line = f.readline()
            else:
                line = f.readline()
            stripped_line = line.strip()
            uppercase_stripped_line = stripped_line.upper()
            if is_comment(stripped_line):
                continue
            if (stripped_line == '' or is_keyword(uppercase_stripped_line)) and data_type_to_read:
                data_type_to_read = ''
                previous_element_number = None
                element_type = ''
                element_set = ''
                generate_element = False
            elif uppercase_stripped_line.startswith('*INCLUDE'):
                keyword, params = parse_keyword_line(stripped_line)
                parent_path = os.path.abspath(os.path.join(path, os.pardir))
                try:
                    path_to_include_file = os.path.join(
                        parent_path, params['INPUT'])
                    include_file = open(path_to_include_file)
                    prev_line_num = line_num + 1
                    line_num = 0
                except KeyError:
                    raise_parser_error(
                        '*INCLUDE definition must have INPUT.',
                        line_num,
                        stripped_line)
            elif is_keyword_with_data(uppercase_stripped_line):
                if stripped_line.endswith(','):
                    raise_parser_error(
                        'Continuation of keyword lines not supported.',
                        line_num,
                        stripped_line)
                data_type_to_read = get_data_type(uppercase_stripped_line)
                keyword, params = parse_keyword_line(stripped_line)
                if 'ELSET' in params:
                    element_set = params['ELSET']
                if 'GENERATE' in params:
                    generate_element = True
                if data_type_to_read == 'element':
                    try:
                        element_type = params['TYPE']
                    except KeyError:
                        raise_parser_error(
                            '*ELEMENT definition must have TYPE.',
                            line_num,
                            stripped_line)
            elif data_type_to_read:
                if data_type_to_read == 'node':
                    node_number, coordinates = parse_node_data_line(
                        stripped_line, line_num)
                    result['node_coordinates_by_number'][node_number] = coordinates
                elif data_type_to_read == 'element':
                    element_data = parse_element_data_line(
                        stripped_line, line_num)
                    if previous_element_number is not None:
                        result['element_dict_by_type'][element_type][previous_element_number].extend(
                            element_data)
                        previous_element_number = None
                    else:
                        element_number = element_data[0]
                        node_numbers = element_data[1:]
                        result['element_dict_by_type'][element_type][element_number] = node_numbers
                        if element_set:
                            result['element_set_by_name'][element_set].add(
                                element_number)
                    if stripped_line.endswith(','):
                        previous_element_number = element_number
                elif data_type_to_read == 'element_set':
                    if ',' not in stripped_line:
                        if stripped_line in result['element_set_by_name']:
                            result['element_set_by_name'][element_set] = result['element_set_by_name'][stripped_line]
                        else:
                            element = int(stripped_line)
                            result['element_set_by_name'][element_set].add(element)
                    else:
                        parts = stripped_line.split(',')
                        if generate_element:
                            num_parts = len(parts)
                            if not 2 <= num_parts <= 3:
                                raise_parser_error(
                                    'GENERATE data line must contain 2 or 3 elements.',
                                    line_num,
                                    stripped_line)
                            if num_parts == 2:
                                start = int(parts[0])
                                end = int(parts[1])
                                elements = {e for e in range(start, end + 1)}
                                result['element_set_by_name'][element_set] = elements
                            else:
                                start = int(parts[0])
                                end = int(parts[1])
                                step = int(parts[2])
                                elements = {e for e in range(
                                    start, end + 1, step)}
                                result['element_set_by_name'][element_set] = elements
                            generate_element = False
                        else:
                            if stripped_line.endswith(','):
                                parts = parts[:-1]
                            for part in parts:
                                if part in result['element_set_by_name']:
                                    if len(result['element_set_by_name'][element_set]) == 0:
                                        result['element_set_by_name'][element_set] = result['element_set_by_name'][part].copy(
                                        )
                                    else:
                                        result['element_set_by_name'][element_set] = result['element_set_by_name'][element_set].union(
                                            result['element_set_by_name'][part])
                                else:
                                    element = int(part)
                                    result['element_set_by_name'][element_set].add(
                                        element)
            line_num += 1
    return result


def parse_node_data_line(node_data_line: str, line_num: int) -> Tuple[int, Tuple[float, float, float]]:
    """Parse a node from a node data line.

    :param node_data_line: Node data line stripped of surrounding white-space.
    :param line_num: Line number.
    :raises ValueError: When number of comma-separated parts doesn't equal 4.
    :return: Two-element tuple containing node number,
             and list of node coordinate values.
    """
    parts = node_data_line.split(',')
    if len(parts) != 4:
        raise_parser_error(
            'Node must have 4 parts: number, 1st coord, 2nd coord, 3rd coord.',
            line_num,
            node_data_line)
    stripped_parts = strip_parts(parts)
    node_number = stripped_parts[0]
    return int(node_number), (
        float(stripped_parts[1]),
        float(stripped_parts[2]),
        float(stripped_parts[3])
    )


def parse_element_data_line(element_data_line: str, line_num: int) -> List[int]:
    """Parse element data from an element data line.

    :param element_data_line: Element data line stripped of surrounding white-space.
    :param line_num: Line number.
    :raises ValueError: When number of comma-separated parts exceeds 16.
    :return: List of integers.
    """
    parts = element_data_line.split(',')
    if element_data_line.endswith(','):
        parts = parts[:-1]
    if len(parts) > 16:
        msg = 'Element on line {} must not exceed 16 parts.'
        msg += '\n    {}'.format(element_data_line)
        raise ValueError(msg.format(line_num))
    return [int(part.strip() or 0) for part in parts]


def strip_parts(parts: List[str]) -> List[str]:
    """Strips parts of a line by removing surrounding white-space.

    CalcluliX is case-insensitive.

    :param parts: Parts of a line.
    :return: Sanitized parts of a line.
    """
    return [part.strip() for part in parts]


def is_keyword(uppercase_stripped_line: str) -> bool:
    """Checks if a line is a keyword definition.

    Keywords in CalculiX input files start with an asterisk '*',
    and comments start with two asterisks '**'.

    :param uppercase_stripped_line: Upper-cased line without surrounding white-space.
    :return: True if the line is a keyword definition, False otherwise.
    """
    return (
        uppercase_stripped_line.startswith('*') and not
        is_comment(uppercase_stripped_line)
    )


def is_comment(stripped_line: str) -> bool:
    """Checks if a line is a comment.

    Keywords in CalculiX input files start with an asterisk '*',
    and comments start with two asterisks '**'.

    :param stripped_line: Line without surrounding white-space.
    :return: True if the line is a keyword definition, False otherwise.
    """
    return stripped_line.startswith('**')


def is_keyword_with_data(uppercase_stripped_line: str) -> bool:
    """Checks if a line is a keyword definition.

    Keywords in CalculiX input files start with an asterisk '*',
    and comments start with two asterisks '**'.

    :param uppercase_stripped_line: Upper-cased line without surrounding white-space.
    :return: True if the line is a keyword definition, False otherwise.
    """
    predicates = get_predicate_by_data_type().values()
    return any([predicate(uppercase_stripped_line) for predicate in predicates])


def is_node_definition(uppercase_stripped_line: str) -> bool:
    """Checks if a line is a node definition.

    :param uppercase_stripped_line: Upper-cased line without surrounding white-space.
    :return: True if the line is a node definition, False otherwise.
    """
    return (
        uppercase_stripped_line.startswith('*NODE') and not
        (
            uppercase_stripped_line.startswith('*NODE FILE') or
            uppercase_stripped_line.startswith('*NODE OUTPUT') or
            uppercase_stripped_line.startswith('*NODE PRINT')
        )
    )


def is_element_definition(uppercase_stripped_line: str) -> bool:
    """Checks if a line is an element definition.

    :param uppercase_stripped_line: Upper-cased line without surrounding white-space.
    :return: True if the line is an element definition, False otherwise.
    """
    return (
        uppercase_stripped_line.startswith('*ELEMENT') and not
        uppercase_stripped_line.startswith('*ELEMENT OUTPUT')
    )


def is_element_set_definition(uppercase_stripped_line: str) -> bool:
    """Checks if a line is an element set definition.

    :param uppercase_stripped_line: Upper-cased line without surrounding white-space.
    :return: True if the line is an element set definition, False otherwise.
    """
    return uppercase_stripped_line.startswith('*ELSET')


def get_data_type(uppercase_stripped_line: str) -> str:
    predicate_by_data_type = get_predicate_by_data_type()
    for data_type, predicate in predicate_by_data_type.items():
        if predicate(uppercase_stripped_line):
            return data_type


def get_predicate_by_data_type() -> Dict[str, Callable[[str], bool]]:
    return {
        'node': is_node_definition,
        'element': is_element_definition,
        'element_set': is_element_set_definition
    }


def parse_keyword_line(stripped_line: str) -> Tuple[str, dict]:
    """Parses a keyword line for the keyword and any parameters.

    Parameters without an explicit value
    are returned in the dictionary with a value of True.

    :param stripped_line: Line without surrounding white-space.
    :return: Two element tuple containing keyword and parameters.
    """
    parameters = {}
    if ',' not in stripped_line:
        return stripped_line, parameters
    parts = stripped_line.split(',')
    keyword = parts[0]
    remaining_parts = parts[1:]
    for part in remaining_parts:
        if '=' in part:
            key, value = strip_parts(part.split('='))
            parameters[key] = value
        else:
            parameters[part] = True
    return keyword, parameters


def raise_parser_error(msg: str, line_num: int, line: str) -> None:
    """Raise a parser error.

    :param msg: Descriptive error message.
    :param line_num: Line number on which the parser error occurred.
    :param line: Line on which the parser error occurred.
    :raises ParserError: Raise a parser error.
    """
    msg += '\n    Line {}: {}'.format(line_num, line)
    raise ParserError(msg)


__all__ = ['read_mesh']
