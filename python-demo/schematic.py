from schematic_types import *

from dataclasses import dataclass


@dataclass
class Schematic:
    # A unique identifier of the schematic.
    schematic_id: SchematicId

    # The input and output pins defined on this schematic.
    input_pins: set[PinId]
    output_pins: set[PinId]

    # A collection mapping each named component of the schematic to its type.
    components: dict[SchematicComponentId, SchematicId]

    # The connections between input / output pins and the child components.
    connections: set[Connection]

    def get_input_connections_for_component(
        self, component_id: SchematicComponentId | SchematicOutput
    ) -> list[Connection]:
        return [
            connection
            for connection in self.connections
            if connection.destination.component == component_id
        ]

    def get_output_connections_for_component(
        self, component_id: SchematicComponentId | SchematicInput
    ) -> list[Connection]:
        return [
            connection
            for connection in self.connections
            if connection.source.component == component_id
        ]


# Hardcoded definition of a nand schematic.
# This schematic does not implement any connections since the logic is hardcoded.
nand_schematic = Schematic(
    schematic_id=SchematicId("NAND"),
    input_pins=set([PinId("in1"), PinId("in2")]),
    output_pins=set([PinId("out")]),
    components={},
    connections=set([]),
)


def build_schematic_id(schematic_id: str) -> SchematicId:
    return SchematicId(schematic_id)


def build_input_pins(pins_names: list[str]) -> set[PinId]:
    return set([PinId(pin) for pin in pins_names])


def build_output_pins(pins_names: list[str]) -> set[PinId]:
    return set([PinId(pin) for pin in pins_names])


def build_schematic_components(
    components: list[tuple[str, str]]
) -> dict[SchematicComponentId, SchematicId]:
    return {SchematicComponentId(name): SchematicId(type) for name, type in components}


def build_connections(
    connection_tuples: list[tuple[tuple[str, str], tuple[str, str]]]
) -> set[Connection]:
    connections: list[Connection] = []
    for (source_name, source_pin), (
        destination_name,
        destination_pin,
    ) in connection_tuples:
        if source_name == "input":
            source_component = SchematicInput()

        else:
            source_component = SchematicComponentId(source_name)

        if destination_name == "output":
            destination_component = SchematicOutput()

        else:
            destination_component = SchematicComponentId(destination_name)

        source = OutputAttachmentPoint(source_component, OutputPinId(source_pin))

        destination = InputAttachmentPoint(
            destination_component, InputPinId(destination_pin)
        )

        connections.append(Connection(source, destination))

    return set(connections)


def build_schematic(
    schematic_id: str,
    input_pins: list[str],
    output_pins: list[str],
    components: list[tuple[str, str]],
    connections: list[tuple[tuple[str, str], tuple[str, str]]],
):
    """
    Construct a new schematic.
    This should be called instead of constructing a schematic yourself.
    This handles all the proper validation checks for a schematic.

    @TODO: Validation
        Ensure all input pins are connected.
        Ensure each input pin only has a single connection.
        Check for circular connections.
    """

    schematic_id = build_schematic_id(schematic_id)
    schematic_input_pins = build_input_pins(input_pins)
    schematic_output_pins = build_output_pins(output_pins)
    schematic_components = build_schematic_components(components)
    schematic_connections = build_connections(connections)

    schematic = Schematic(
        schematic_id=schematic_id,
        input_pins=schematic_input_pins,
        output_pins=schematic_output_pins,
        components=schematic_components,
        connections=schematic_connections,
    )

    return schematic
