from enum import Enum
from dataclasses import dataclass

import itertools


# Unique identifier for a component.
class ComponentId(str):
    pass


# Local variable name for a component from within component a schematic.
class PartId(str):
    pass


# A local variable name for a pin from within component a schematic.
class PinId(str):
    pass


# An identifier for either the input or output a component schematic.
class PartIoId(Enum):
    INPUT = "Input"
    OUTPUT = "Output"


# An identifier for a pin on a component.
# The pin can either be a partId meaning it's referencing a pin on a child component
# or it can be a PartIoId meaning it's referencing the input or output of the current schematic
@dataclass
class PartPin:
    part: PartId | PartIoId
    pin: PinId

    def __hash__(self) -> int:
        return hash((self.part, self.pin))


# Object used to describe a connection between two pins.
@dataclass
class Connection:
    source: PartPin
    target: PartPin

    def __hash__(self) -> int:
        return hash((self.source, self.target))


# A component schematic.
@dataclass
class Component:
    id: ComponentId
    input_pins: list[PinId]
    output_pins: list[PinId]
    parts: dict[PartId, ComponentId]
    connections: list[Connection]


class ComponentLibrary:
    components: list[Component]

    def __init__(self):
        self.components = [nand_component]

    def add_component(self, component: Component):
        if self.get_component_or_none(component.id) is not None:
            raise Exception(f"Component {component.id} already exists in library.")

        self.components.append(component)

    def get_component_or_none(self, component_id: ComponentId) -> Component | None:
        for component in self.components:
            if component.id == component_id:
                return component

        return None

    def get_component(self, component_id: ComponentId) -> Component:
        component = self.get_component_or_none(component_id)
        if component is None:
            raise Exception(f"Component {component_id} not found")

        return component

    def simulate_component(
        self, component: Component, inputs: dict[PinId, bool]
    ) -> dict[PinId, bool]:

        if component.id == ComponentId("NAND"):
            return simulate_nand(inputs)

        connections: list[Connection] = component.connections
        parts = self.get_component_parts(component)

        resolved_part_ids: dict[PartId, dict[PinId, bool]] = {}
        resolved_connections: dict[Connection, bool] = {}

        # Resolve any input connections.
        input_connections = [
            connection
            for connection in connections
            if connection.source.part == PartIoId.INPUT
        ]
        for input_connection in input_connections:
            resolved_connections[input_connection] = inputs[input_connection.source.pin]

        # Loop until we have resolved all output connections
        while True:
            # Iterate through each unresolved part.
            for part_id in parts:
                part = parts[part_id]

                # If the part has already been resolved, skip it.
                if part_id in resolved_part_ids:
                    continue

                # Check if all the input connections of the part have been resolved
                part_input_connections = [
                    connection
                    for connection in connections
                    if connection.target.part == part_id
                ]

                if all(
                    connection in resolved_connections
                    for connection in part_input_connections
                ):
                    part_inputs: dict[PinId, bool] = {
                        connection.target.pin: resolved_connections[connection]
                        for connection in part_input_connections
                    }

                    # Resolve the part.
                    resolved_part_ids[part_id] = self.simulate_component(
                        part, part_inputs
                    )

                    # Resolve all output connections of the part.
                    output_connections = [
                        connection
                        for connection in connections
                        if connection.source.part == part_id
                    ]

                    for output_connection in output_connections:
                        resolved_connections[output_connection] = resolved_part_ids[
                            part_id
                        ][output_connection.source.pin]

            # If all output connections have been resolved, we're done.
            output_connections = [
                connection
                for connection in connections
                if connection.target.part == PartIoId.OUTPUT
            ]

            if all(
                connection in resolved_connections for connection in output_connections
            ):
                results = {
                    connection.target.pin: resolved_connections[connection]
                    for connection in output_connections
                }

                # print(f"Results for component {component.id} with input {inputs} -> {results}")
                return results

    def get_component_truth_table(
        self, component: Component
    ) -> list[tuple[dict[PinId, bool], dict[PinId, bool]]]:
        input_pins = component.input_pins

        input_combinations = list(
            itertools.product([False, True], repeat=len(input_pins))
        )
        pin_combinations: list[dict[PinId, bool]] = [
            dict(zip(input_pins, combination)) for combination in input_combinations
        ]

        output_results: list[tuple[dict[PinId, bool], dict[PinId, bool]]] = []
        for pin_combination in pin_combinations:
            output_results.append(
                (pin_combination, self.simulate_component(component, pin_combination))
            )

        return output_results

    def get_component_parts(self, component: Component) -> dict[PartId, Component]:
        parts: dict[PartId, Component] = {
            part_id: self.get_component(component.parts[part_id])
            for part_id in component.parts
        }
        return parts



nand_component = Component(
    id=ComponentId("NAND"),
    input_pins=[PinId("in1"), PinId("in2")],
    output_pins=[PinId("out")],
    parts={},
    connections=[],
)


# The only hardcoded component.
# All other components must be built from nand gates.
def simulate_nand(inputs: dict[PinId, bool]) -> dict[PinId, bool]:
    results = {PinId("out"): not (inputs[PinId("in1")] and inputs[PinId("in2")])}
    # print(f"Results for component NAND with input {inputs} -> {results}")
    return results
