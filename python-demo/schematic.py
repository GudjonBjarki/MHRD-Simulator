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


def build_schematic(
    schematic_id: SchematicId,
    input_pins: set[PinId],
    output_pins: set[PinId],
    components: dict[SchematicComponentId, SchematicId],
    connections: set[Connection],
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

    schematic = Schematic(
        schematic_id=schematic_id,
        input_pins=input_pins,
        output_pins=output_pins,
        components=components,
        connections=connections,
    )

    return schematic
