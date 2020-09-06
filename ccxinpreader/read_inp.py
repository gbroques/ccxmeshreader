from collections import defaultdict
from typing import List, Tuple


def read_inp(path: str) -> dict:
    """Reads a CalculiX input file.

    :param path: Path to CalculiX input file.
    :return: a dictionary with nodes and elements.
    """
    result = {
        'nodes': {},
        'elements': defaultdict(dict)
    }
    with open(path, 'r') as f:
        line = f.readline()
        line_num = 1
        data_type = ''
        previous_element_number = None
        element_type = ''
        while line:
            sanitized_line = sanitize_line(line)
            if (sanitized_line == '' or is_keyword(sanitized_line)) and data_type:
                data_type = ''
                previous_element_number = None
                element_type = ''
            elif is_keyword_with_data(sanitized_line):
                data_type = get_data_type(sanitized_line)
                keyword, params = parse_keyword_line(sanitized_line)
                if data_type == 'element':
                    try:
                        element_type = params['TYPE']
                    except KeyError:
                        msg = 'Element definition on line {} must have TYPE.'
                        msg += '\n    {}'.format(sanitized_line)
                        raise ValueError(msg.format(line_num))
            elif data_type:
                if data_type == 'node':
                    node_number, data = parse_node_data_line(
                        sanitized_line, line_num)
                    result['nodes'][node_number] = data
                elif data_type == 'element':
                    element_data = parse_element_data_line(
                        sanitized_line, line_num)
                    if previous_element_number is not None:
                        result['elements'][element_type][previous_element_number].extend(
                            element_data)
                        previous_element_number = None
                    else:
                        element_number = element_data[0]
                        node_numbers = element_data[1:]
                        result['elements'][element_type][element_number] = node_numbers
                    if sanitized_line.endswith(','):
                        previous_element_number = element_number
            line = f.readline()
            line_num += 1
    return result


def parse_node_data_line(node_data_line: str, line_num: int) -> Tuple[int, List[float]]:
    """Parse a node from a node data line.

    :param node_data_line: Sanitized node data line.
    :param line_num: Line number.
    :raises ValueError: When number of comma-separated parts doesn't equal 4.
    :return: Two-element tuple containing node number,
             and list of node coordinate values.
    """
    parts = node_data_line.split(',')
    if len(parts) != 4:
        msg = 'Node on line {} must have 4 parts: number, 1st coord, 2nd coord, 3rd coord.'
        msg += '\n    {}'.format(node_data_line)
        raise ValueError(msg.format(line_num))
    sanitized_parts = sanitize_parts(parts)
    node_number = sanitized_parts[0]
    return int(node_number), [
        float(sanitized_parts[1]),
        float(sanitized_parts[2]),
        float(sanitized_parts[3])
    ]


def parse_element_data_line(element_data_line: str, line_num: int) -> List[int]:
    """Parse element data from an element data line.

    :param element_data_line: Sanitized element data line.
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
    return [int(part.strip()) for part in parts]


def sanitize_line(line: str) -> str:
    """Sanitizes a line by removing surrounding white-space and upper-casing.

    CalcluliX is case-insensitive.

    :param line: Line from input file.
    :return: Sanitized line.
    """
    return line.strip().upper()


def sanitize_parts(parts: List[str]) -> List[str]:
    """Sanitizes parts of a line by removing surrounding white-space.

    CalcluliX is case-insensitive.

    :param parts: Parts of a line.
    :return: Sanitized parts of a line.
    """
    return [part.strip() for part in parts]


def is_keyword(sanitized_line: str) -> bool:
    """Checks if a sanitized line is a keyword definition.

    Keywords in CalculiX input files start with an asterisk '*',
    and comments start with two asterisks '**'.

    :param sanitized_line: Upper-cased line without surrounding white-space.
    :return: True if the line is a keyword definition, False otherwise.
    """
    return (
        sanitized_line.startswith('*') and not
        sanitized_line.startswith('**')
    )


def is_keyword_with_data(sanitized_line: str) -> bool:
    """Checks if a sanitized line is a keyword definition.

    Keywords in CalculiX input files start with an asterisk '*',
    and comments start with two asterisks '**'.

    :param sanitized_line: Upper-cased line without surrounding white-space.
    :return: True if the line is a keyword definition, False otherwise.
    """
    predicates = [is_node_definition, is_element_definition]
    return any([predicate(sanitized_line) for predicate in predicates])


def is_node_definition(sanitized_line: str) -> bool:
    """Checks if a sanitized line is a node definition.

    :param sanitized_line: Upper-cased line without surrounding white-space.
    :return: True if the line is a node definition, False otherwise.
    """
    return (
        sanitized_line.startswith('*NODE') and not
        (
            sanitized_line.startswith('*NODE FILE') or
            sanitized_line.startswith('*NODE OUTPUT') or
            sanitized_line.startswith('*NODE PRINT')
        )
    )


def is_element_definition(sanitized_line: str) -> bool:
    """Checks if a sanitized line is an element definition.

    :param sanitized_line: Upper-cased line without surrounding white-space.
    :return: True if the line is an element definition, False otherwise.
    """
    return (
        sanitized_line.startswith('*ELEMENT') and not
        sanitized_line.startswith('*ELEMENT OUTPUT')
    )


def get_data_type(sanitized_keyword_line: str) -> str:
    predicate_by_data_type = {
        'node': is_node_definition,
        'element': is_element_definition
    }
    for data_type, predicate in predicate_by_data_type.items():
        if predicate(sanitized_keyword_line):
            return data_type


def parse_keyword_line(sanitized_line: str) -> Tuple[str, dict]:
    """Parses a keyword line for the keyword and any parameters.

    Parameters without an explicit value
    are returned in the dictionary with a value of True.

    :param sanitized_line: Upper-cased line without surrounding white-space.
    :return: Two element tuple containing keyword and parameters.
    """
    parameters = {}
    if ',' not in sanitized_line:
        return sanitized_line, parameters
    parts = sanitized_line.split(',')
    keyword = parts[0]
    remaining_parts = parts[1:]
    for part in remaining_parts:
        if '=' in part:
            key, value = sanitize_parts(part.split('='))
            parameters[key] = value
        else:
            parameters[part] = True
    return keyword, parameters


__all__ = ['read_inp']
