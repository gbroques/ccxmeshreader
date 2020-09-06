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
        read_node = False
        while line:
            sanitized_line = sanitize_line(line)
            if is_node_definition(sanitized_line):
                read_node = True
            elif (
                (sanitized_line == '' or sanitized_line.startswith('*')) and
                (read_node and not is_node_definition(sanitized_line))
            ):
                read_node = False
            elif read_node:
                parts = line.split(',')
                if len(parts) != 4:
                    msg = 'Node on line {} must have 4 parts: number, 1st coord, 2nd coord, 3rd coord.'
                    msg += '\n    {}'.format(sanitized_line)
                    raise ValueError(msg.format(line_num))
                sanitized_parts = sanitize_parts(parts)
                node_number = sanitized_parts[0]
                result['nodes'][node_number] = [
                    sanitized_parts[1],
                    sanitized_parts[2],
                    sanitized_parts[3]
                ]
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


__all__ = ['read_inp']
