from typing import Callable

from schematic import Schematic, build_schematic


def filter_string(input_string: str, filter_function: Callable[[str], bool]) -> str:
    output_list = filter(filter_function, input_string)
    output_string = "".join(output_list)
    return output_string


def string_after_literal(input_string: str, literal: str) -> str | None:
    """
    Returns the string after the first occurence of the literal.
    If the literal is not found, returns None.
    """
    literal_index = input_string.find(literal)
    if literal_index == -1:
        return None

    index_after_literal = literal_index + len(literal)
    string_after_literal = input_string[index_after_literal:]
    return string_after_literal


def string_before_literal(input_string: str, literal: str) -> str | None:
    """
    Returns the string before the first occurence of the literal.
    If the literal is not found, returns None.
    """
    literal_index = input_string.find(literal)
    if literal_index == -1:
        return None

    string_before_literal = input_string[0:literal_index]
    return string_before_literal


def string_between_literals(
    input_string: str, start_literal: str, stop_literal: str
) -> str | None:
    """
    Returns the string between the first occurence of the start literal and the first occurence of the stop literal.
    If either literal is not found, returns None.
    """
    string_after_start = string_after_literal(input_string, start_literal)
    if string_after_start is None:
        return None

    string_before_stop = string_before_literal(string_after_start, stop_literal)
    if string_before_stop is None:
        return None

    return string_before_stop


def parse_name_section(name_section: str) -> str:
    name = string_between_literals(name_section, '"', '"')
    if name is None:
        raise Exception("Name was not found in name section.")
    return name


def parse_list(list_string: str) -> list[str]:
    list_entries = list_string.split(",")
    return list_entries


parse_input_section = parse_list
parse_output_section = parse_list


def parse_components(components_section: str) -> list[tuple[str, str]]:
    components: list[tuple[str, str]] = []
    component_definitions = components_section.split(",")
    for component in component_definitions:
        try:
            component_name, component_type = component.split("->")

        except ValueError:
            raise Exception("Invalid component definition: " + component)

        components.append((component_name, component_type))

    return components


def parse_connections(
    connections_section: str,
) -> list[tuple[tuple[str, str], tuple[str, str]]]:
    connections: list[tuple[tuple[str, str], tuple[str, str]]] = []
    connection_definitions = connections_section.split(",")

    for connection_definition in connection_definitions:
        try:
            source, destination = connection_definition.split("->")
            source_name, source_pin = source.split(".")
            destination_name, destination_pin = destination.split(".")

        except ValueError:
            raise Exception("Invalid connection definition: " + connection_definition)

        connections.append(
            ((source_name, source_pin), (destination_name, destination_pin))
        )

    return connections


def parse_mhrd_schematic(mhrd_string: str) -> Schematic:
    clean_text = filter_string(mhrd_string, (lambda c: not c.isspace()))

    # parse name
    name_section = string_between_literals(clean_text, "Name:", ";")
    if name_section is None:
        raise Exception("Name section not found!")

    schematic_name = parse_name_section(name_section)

    # Parse inputs
    input_section = string_between_literals(clean_text, "Inputs:", ";")
    if input_section is None:
        raise Exception("Inputs section not found!")

    schematic_input_pins = parse_input_section(input_section)

    # Parse outputs
    output_section = string_between_literals(clean_text, "Outputs:", ";")
    if output_section is None:
        raise Exception("Outputs section not found!")

    schematic_output_pins = parse_output_section(output_section)

    # Parse components.
    component_section = string_between_literals(clean_text, "Parts:", ";")
    if component_section is None:
        raise Exception("Components section not found!")

    schematic_components = parse_components(component_section)

    # Parse connections.
    connection_section = string_between_literals(clean_text, "Wires:", ";")
    if connection_section is None:
        raise Exception("Connections section not found!")

    schematic_connections = parse_connections(connection_section)

    return build_schematic(
        schematic_name,
        schematic_input_pins,
        schematic_output_pins,
        schematic_components,
        schematic_connections,
    )
