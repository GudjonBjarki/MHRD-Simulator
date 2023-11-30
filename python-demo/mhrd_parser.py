from typing import Callable


class TextParser:
    content: str
    index: int

    def __init__(self, content: str):
        self.content = content
        self.index = 0

    def peek(self) -> str | None:
        try:
            return self.content[self.index]
        except IndexError:
            return None

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

    def parse_whitespace(self) -> str:
        """
        Parse whitespace characters or comments starting with "//" until the end of the line.
        """
        whitespace = ""

        while True:
            if self.peek().isspace():
                whitespace += self.getch()

            elif self.peekn(2) == "//":
                while self.peek() != "\n":
                    self.getch()

            else:
                break
        
        return whitespace
    
    def parse_span(self, span_lambda: Callable[[str], bool]) -> str:
        """
        Parse a span of characters until a character is found that the span_lambda returns false for.
        """
        span = ""

        while True:
            next_char = self.peek()
            if next_char is None:
                break

            if not span_lambda(next_char):
                break

            span += self.getch()

        return span
    
    def parse_literal(self, literal: str) -> str | None:
        """
        Parse a literal string.
        """
        if self.peekn(len(literal)) == literal:
            return self.getchn(len(literal))

        else:
            return None
    
    def goto_literal(self, literal: str) -> bool:
        """
        Go to the first occurance of a literal string.
        If the string is found the index of the parser will be set to the start.
        True is returned if the string is found and the index is set, False otherwise.
        """
        index = self.content.find(literal)
        if index == -1:
            return False
        
        self.index = index
        return True

def find_section(section_name: str, parser: TextParser) -> str:
    """
    Find a section from a parser containing a MHRD file.
    A secion in a MHRD file is defined as starting with "<sectionName>:" and it's contents being any text that follow up to a semicolon.
    """
    section_header = section_name + ":"

    if not parser.goto_literal(section_header):
        raise Exception(f"{section_name} section not found in MHRD")
    
    parser.parse_literal(section_header)
    
    section_content = parser.parse_span(lambda c : c != ";")
    return section_content

def parse_name(name_section_content: str) -> str:
    parser = TextParser(name_section_content)

    parser.parse_whitespace()
    opening_quote = parser.parse_literal("\"")
    if opening_quote is None:
        raise Exception("Opening quote not found in name section.")
    
    name = parser.parse_span(lambda c : c != "\"")

    closing_quote = parser.parse_literal("\"")
    if closing_quote is None:
        raise Exception("Closing quote not found in name section.")
    
    return name

def parse_inputs(inputs_section_content: str) -> list[str]:
    inputs = inputs_section_content.split(",")
    clean_inputs = [i.lstrip().strip() for i in inputs]
    return clean_inputs

def parse_outputs(outputs_section_content: str) -> list[str]:
    outputs = outputs_section_content.split(",")
    clean_outputs = [i.lstrip().strip() for i in outputs]
    return clean_outputs

def parse_components(components_section_content: str) -> list[tuple[str, str]]:

    component_lines = components_section_content.split(",")
    components: list[tuple[str, str]]= []

    for line_num, component_line  in enumerate(component_lines):
        line_parser = TextParser(component_line)
        line_parser.parse_whitespace()

        component_name = line_parser.parse_span(lambda c : c.isalnum())
        line_parser.parse_whitespace()

        arrow = line_parser.parse_literal("->")
        if arrow is None:
            raise Exception(f"No arrow found in component definition {line_num}. \"{repr(component_line)}\"")
        
        line_parser.parse_whitespace()
        component_schematic = line_parser.parse_span(lambda c: c.isalnum())

        components.append((component_name, component_schematic)) 

    return components

def parse_wires(wires_section_conent: str) -> list[tuple[tuple[str, str], tuple[str, str]]]:
    wire_lines = wires_section_conent.split(",")
    wires: list[tuple[tuple[str, str], tuple[str, str]]] = []

    isalnum_lambda: Callable[[str], bool] = lambda c : c.isalnum()

    for line_num, wire_line in enumerate(wire_lines):
        line_parser = TextParser(wire_line)
        line_parser.parse_whitespace()

        output_component_name = line_parser.parse_span(isalnum_lambda)
        output_component_dot = line_parser.parse_literal(".")
        if output_component_dot is None:
            raise Exception(f"No dot found in output of wire definition {line_num}. {repr(wire_line)}")
            
        output_component_schematic = line_parser.parse_span(isalnum_lambda)
        line_parser.parse_whitespace()

        arrow = line_parser.parse_literal("->")
        if arrow is None:
            raise Exception(f"No arrow found in wire definition {line_num}. {repr(wire_line)}")
        line_parser.parse_whitespace()

        input_component_name = line_parser.parse_span(isalnum_lambda)
        input_component_dot = line_parser.parse_literal(".")
        if input_component_dot is None:
            raise Exception(f"No dot found in input of wire definition {line_num}. {repr(wire_line)}")
        input_component_schematic = line_parser.parse_span(isalnum_lambda)

        wires.append(
            ((output_component_name, output_component_schematic), (input_component_name, input_component_schematic))
        )

    return wires

def parse_mhrd(mhrd_content: str):
    parser = TextParser(mhrd_content)

    # Parse name section.
    name_section_content = find_section("Name", parser)
    schematic_name = parse_name(name_section_content)
    print(schematic_name)

    # Parse the inputs section.
    inputs_section_content = find_section("Inputs", parser)
    schematic_input_pins = parse_inputs(inputs_section_content)
    print(schematic_input_pins)
    
    # Parse the outputs section.
    outputs_section_content = find_section("Outputs", parser)
    schematic_output_pins = parse_outputs(outputs_section_content)
    print(schematic_output_pins)

    # Parse the parts section. 
    parts_section_content = find_section("Parts", parser)
    schematic_components = parse_components(parts_section_content)
    print(schematic_components)
    
    # Parse the Wires section.
    wires_section_content = find_section("Wires", parser)
    schematic_wires = parse_wires(wires_section_content)
    print(schematic_wires)

with open("../schematics/DEMUX-2-1.mhrd", "r") as f:
    content = f.read()

parse_mhrd(content)