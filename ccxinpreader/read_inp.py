from typing import List


def read_inp(path: str) -> dict:
    """Reads a CalculiX input file.

    :param path: Path to CalculiX input file.
    :return: a dictionary with nodes and elements.
    """
    result = {
        'nodes': {},
        'elements': {}
    }
    with open(path, 'r') as f:
        line = f.readline()
        line_num = 1
        data_type = ''
        previous_element_number = None
        while line:
            sanitized_line = sanitize_line(line)
            if (sanitized_line == '' or is_keyword(sanitized_line)) and data_type:
                data_type = ''
            elif is_keyword_with_data(sanitized_line):
                data_type = get_data_type(sanitized_line)
            elif data_type:
                if data_type == 'node':
                    parts = sanitized_line.split(',')
                    if len(parts) != 4:
                        msg = 'Node on line {} must have 4 parts: number, 1st coord, 2nd coord, 3rd coord.'
                        msg += '\n    {}'.format(sanitized_line)
                        raise ValueError(msg.format(line_num))
                    sanitized_parts = sanitize_parts(parts)
                    node_number = sanitized_parts[0]
                    result['nodes'][node_number] = [
                        float(sanitized_parts[1]),
                        float(sanitized_parts[2]),
                        float(sanitized_parts[3])
                    ]
                elif data_type == 'element':
                    parts = sanitized_line.split(',')
                    if sanitized_line.endswith(','):
                        parts = parts[:-1]
                    if len(parts) > 16:
                        msg = 'Element on line {} must not exceed 16 parts.'
                        msg += '\n    {}'.format(sanitized_line)
                        raise ValueError(msg.format(line_num))
                    sanitized_parts = sanitize_parts(parts)
                    element_number = sanitized_parts[0]
                    if not previous_element_number:
                        result['elements'][element_number] = sanitized_parts[1:]
                    else:
                        result['elements'][previous_element_number] = sanitized_parts[1:]
                        previous_element_number = None
                    if sanitized_line.endswith(','):
                        previous_element_number = element_number
            line = f.readline()
            line_num += 1
    return result


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


__all__ = ['read_inp']
