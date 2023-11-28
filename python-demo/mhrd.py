"""
Module to parse circuits from MHDR files.
"""

from typing import Callable
from components import *

"""
[]: Optional
ws: whitepace
<>: Placeholder


MHDR file format:

Name:[ws]"<name>"[ws];[ws]

Inputs:[ws]<pinId1>[ws],[ws]<pinId2>[ws],[ws]...<pinIdN>[ws];[ws]

Outputs:[ws]<pinId1>[ws],[ws]<pinId2>[ws],[ws]...<pinIdN>[ws];[ws]

Parts:[ws]<partId1>[ws]->[ws]<partType1>[ws],[ws]<partId2>[ws]->[ws]<partType2>[ws],[ws]...<partIdN>[ws]->[ws]<partTypeN>[ws];[ws]

Wires:[ws]<partId | IO>[ws].[ws]<pinId>[ws]->[ws]<partId | IO>[ws].[ws]<pinId>[ws],[ws]<partId | IO>[ws].[ws]<pinId>[ws]->[ws]<partId | IO>[ws].[ws]<pinId>[ws],[ws]...<partId | IO>[ws].[ws]<pinId>[ws]->[ws]<partId | IO>[ws].[ws]<pinId>[ws];[ws]
"""


class ParserIter:
    content: str
    index: int

    def __init__(self, content: str):
        self.content = content
        self.index = 0

    def peek(self) -> str:
        return self.content[self.index]

    def peekn(self, n: int) -> str:
        return self.content[self.index : self.index + n]

    def getch(self) -> str:
        char = self.content[self.index]
        self.index += 1
        return char

    def getchn(self, n: int) -> str:
        chars = self.content[self.index : self.index + n]
        self.index += n
        return chars


def parse_whitespace(parser: ParserIter) -> str:
    # Parse whitespace characters or comments starting with "//"" to the end of line
    whitespace = ""

    while True:
        if parser.peek().isspace():
            whitespace += parser.getch()

        elif parser.peekn(2) == "//":
            while parser.peek() != "\n":
                parser.getch()

        else:
            break

    return whitespace


def parse_span(parser: ParserIter, span_lambda: Callable[[str], bool]) -> str:
    span = ""

    while span_lambda(parser.peek()):
        span += parser.getch()

    return span


def parse_literal(parser: ParserIter, literal: str) -> str | None:
    if parser.peekn(len(literal)) == literal:
        return parser.getchn(len(literal))

    else:
        return None


def parse_name(parser: ParserIter) -> str:
    # [ws]Name:[ws]"<name>"[ws];[ws]

    parse_whitespace(parser)
    header = parse_literal(parser, "Name:")
    if header is None:
        raise ValueError("Expected literal 'Name:' while parsing name")

    parse_whitespace(parser)
    open_quote = parse_literal(parser, '"')
    if open_quote is None:
        raise ValueError("Expected opening quote while parsing name")

    name = parse_span(parser, lambda char: char != '"')

    close_quote = parse_literal(parser, '"')
    if close_quote is None:
        raise ValueError("Expected closing quote while parsing name")

    parse_whitespace(parser)
    semicolon = parse_literal(parser, ";")
    if semicolon is None:
        raise ValueError("Expected semicolon while parsing name")

    parse_whitespace(parser)
    return name


def parse_input_pins(parser: ParserIter) -> list[str]:
    parse_whitespace(parser)

    header = parse_literal(parser, "Inputs:")
    if header is None:
        raise ValueError("Expected literal 'Inputs:' while parsing input pins")

    pins: list[str] = []

    while True:
        parse_whitespace(parser)

        pin = parse_span(
            parser, lambda char: char != "," and char != ";" and not char.isspace()
        )
        pins.append(pin)

        comma = parse_literal(parser, ",")
        if comma is None:
            break

    parse_whitespace(parser)

    semicolon = parse_literal(parser, ";")
    if semicolon is None:
        raise ValueError("Expected semicolon while parsing input pins")

    return pins


def parse_output_pins(parser: ParserIter) -> list[str]:
    parse_whitespace(parser)

    header = parse_literal(parser, "Outputs:")
    if header is None:
        raise ValueError("Expected literal 'Outputs:' while parsing output pins")

    pins: list[str] = []

    while True:
        parse_whitespace(parser)

        pin = parse_span(
            parser, lambda char: char != "," and char != ";" and not char.isspace()
        )
        pins.append(pin)

        comma = parse_literal(parser, ",")
        if comma is None:
            break

    parse_whitespace(parser)

    semicolon = parse_literal(parser, ";")
    if semicolon is None:
        raise ValueError("Expected semicolon while parsing output pins")

    return pins


def parse_parts(parser: ParserIter) -> list[tuple[str, str]]:
    parse_whitespace(parser)

    header = parse_literal(parser, "Parts:")
    if header is None:
        raise ValueError("Expected literal 'Parts:' while parsing parts")

    parse_whitespace(parser)

    parts: list[tuple[str, str]] = []

    while True:
        parse_whitespace(parser)

        part_id = parse_span(
            parser, lambda char: char != "-" and char != ";" and not char.isspace()
        )

        parse_whitespace(parser)

        arrow = parse_literal(parser, "->")
        if arrow is None:
            raise ValueError("Expected arrow while parsing parts")

        parse_whitespace(parser)

        part_type = parse_span(
            parser, lambda char: char != "," and char != ";" and not char.isspace()
        )

        parts.append((part_id, part_type))

        comma = parse_literal(parser, ",")
        if comma is None:
            break

    parse_whitespace(parser)

    semicolon = parse_literal(parser, ";")
    if semicolon is None:
        raise ValueError("Expected semicolon while parsing parts")


    return parts


def parse_wires(parser: ParserIter) -> list[tuple[tuple[str, str], tuple[str, str]]]:
    parse_whitespace(parser)

    header = parse_literal(parser, "Wires:")
    if header is None:
        raise ValueError("Expected literal 'Wires:' while parsing wires")

    parse_whitespace(parser)

    wires: list[tuple[tuple[str, str], tuple[str, str]]] = []

    while True:
        parse_whitespace(parser)

        source_part_id = parse_span(
            parser, lambda char: char != "." and char != ";" and not char.isspace()
        )

        parse_whitespace(parser)

        dot = parse_literal(parser, ".")
        if dot is None:
            raise ValueError("Expected dot while parsing wires")

        parse_whitespace(parser)

        source_pin_id = parse_span(
            parser, lambda char: char != "-" and char != ";" and not char.isspace()
        )

        parse_whitespace(parser)

        arrow = parse_literal(parser, "->")
        if arrow is None:
            raise ValueError("Expected arrow while parsing wires")

        parse_whitespace(parser)

        destination_part_id = parse_span(
            parser, lambda char: char != "." and char != ";" and not char.isspace()
        )

        parse_whitespace(parser)

        dot = parse_literal(parser, ".")
        if dot is None:
            raise ValueError("Expected dot while parsing wires")

        parse_whitespace(parser)

        destination_pin_id = parse_span(
            parser, lambda char: char != "," and char != ";" and not char.isspace()
        )

        wires.append(
            ((source_part_id, source_pin_id), (destination_part_id, destination_pin_id))
        )

        comma = parse_literal(parser, ",")
        if comma is None:
            break

    return wires


def parse_script(script: str) -> Component:
    parser = ParserIter(script)

    name = parse_name(parser)
    input_pins = parse_input_pins(parser)
    output_pins = parse_output_pins(parser)
    parts = parse_parts(parser)
    wires = parse_wires(parser)

    component_id = ComponentId(name)
    input_pin_ids = [PinId(pin) for pin in input_pins]
    output_pin_ids = [PinId(pin) for pin in output_pins]
    part_dict = {
        PartId(part[0]): ComponentId(part[1])
        for part in parts
    }

    connections: list[Connection] = []
    for wire in wires:
        wire_source = wire[0]
        wire_destination = wire[1]

        if wire_source[0] == "input":
            wire_source_part = PartIoId.INPUT

        elif wire_source[0] == "output":
            wire_source_part = PartIoId.OUTPUT
        
        else:
            wire_source_part = PartId(wire_source[0])

        if wire_destination[0] == "input":
            wire_destination_part = PartIoId.INPUT
        
        elif wire_destination[0] == "output":
            wire_destination_part = PartIoId.OUTPUT

        else:
            wire_destination_part = PartId(wire_destination[0])

        wire_source_pin = PinId(wire_source[1])
        wire_destination_pin = PinId(wire_destination[1])

        connection = Connection(
            PartPin(wire_source_part, wire_source_pin),
            PartPin(wire_destination_part, wire_destination_pin)
        )
        connections.append(connection)

    return Component(
        id=component_id,
        input_pins=input_pin_ids,
        output_pins=output_pin_ids,
        parts=part_dict,
        connections=connections,
    )
