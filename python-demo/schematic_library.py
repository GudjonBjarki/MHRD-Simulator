from schematic_types import *
from schematic import Schematic, nand_schematic

class SchematicLibrary:
    schematics: list[Schematic]

    def __init__(self):
        self.schematics = [nand_schematic]

    def get_schematic_or_none(self, schematic_id: SchematicId) -> Schematic | None:
        """
        Fetch a schematic by its id.
        If the requested schematic is not found, return None.
        """
        for schematic in self.schematics:
            if schematic.schematic_id == schematic_id:
                return schematic
        return None
    
    def get_schematic(self, schematic_id: SchematicId) -> Schematic:
        """
        Fetch a schematic by its id.
        If the requested schematic is not found, raise an exception.
        """
        schematic = self.get_schematic_or_none(schematic_id)
        if schematic is None:
            raise Exception(f"Could not find schematic with id: {schematic_id}")
        return schematic

    def add_schematic(self, schematic: Schematic) -> None:
        """
        Add a schematic to the library.
        """
        if self.get_schematic_or_none(schematic.schematic_id) is not None:
            raise Exception(f"Cannot add schematic with duplicate id: {schematic.schematic_id}")

        self.schematics.append(schematic)

    def simulate_schematic(self, schematic: Schematic, input_signals: dict[OutputPinId, bool]) -> dict[InputPinId, bool]:
        # verify that the input signals are valid
        verify_schematic_signal_pins(schematic, input_signals)

        # If we're trying to simulate a NAND use the hardcoded logic function.
        if schematic.schematic_id == SchematicId("NAND"):
            return nand_logic(input_signals)

        # fetch each component used in the schematic.
        components = get_schematic_components(schematic, self)

        # Initialize the signal state of the schematic.
        # All signals will start as unresolved (None)
        connection_signal_state: dict[Connection, bool | None] = {
            connection: None
            for connection in schematic.connections
        }

        # Resolve the input signals for the schematic from the input_signals dict.
        circuit_input_connections = get_output_connections_for_component(schematic, SchematicInput())
        for connection in circuit_input_connections:
            connection_signal_state[connection] = input_signals[connection.source.pin]

        # Loop until all output signals have been resolved.
        while True:

            # Loop through each component in the schematic.
            for component_id, component_schematic in components.items():

                # If all the output signals for the component are resolved, skip it.
                component_output_connections = get_output_connections_for_component(schematic, component_id)
                if are_connections_resolved(schematic, component_output_connections, connection_signal_state):
                    continue

                # If all the input signals for the component are resolved we're able to simulate it.
                component_input_connections = get_input_connections_for_component(schematic, component_id)
                if are_connections_resolved(schematic, component_input_connections, connection_signal_state):

                    # Parse the signals so they can be passed to the simulation function
                    component_simulation_input_signals: dict[OutputPinId, bool] = {
                        OutputPinId(connection.destination.pin): connection_signal_state[connection] # type: ignore
                        for connection in component_input_connections
                    }

                    # Simulate the component
                    component_simulation_output_signals = self.simulate_schematic(component_schematic, component_simulation_input_signals)

                    # Update the signal state for the component's output signals
                    for connection in component_output_connections:
                        connection_signal_state[connection] = component_simulation_output_signals[InputPinId(connection.source.pin)]

            # If all the output signals for the schematic are resolved we're done.
            circuit_output_signals = get_input_connections_for_component(schematic, SchematicOutput())
            if are_connections_resolved(schematic, circuit_output_signals, connection_signal_state):
                return {
                    InputPinId(connection.destination.pin): connection_signal_state[connection] # type: ignore
                    for connection in circuit_output_signals
                }



def nand_logic(input_signals: dict[OutputPinId, bool]):
    """
    The hardcoded logic for a nand gate.
    """
    return {
        InputPinId("out"): (input_signals[OutputPinId("in1")] and input_signals[OutputPinId("in2")])
    } 

def verify_schematic_signal_pins(schematic: Schematic, input_signals: dict[OutputPinId, bool]) -> None:
    """
    Verify all input signals provided are defined on the schematic and that there are no extra signals.
    """
    for pin_id in input_signals:
        if pin_id not in schematic.input_pins:
            raise Exception(f"Input signal {pin_id} is not defined on schematic {schematic.schematic_id}")
        
    for pin_id in schematic.input_pins:
        if pin_id not in input_signals:
            raise Exception(f"Input signal {pin_id} is not provided for schematic {schematic.schematic_id}")

def get_schematic_components(schematic: Schematic, library: SchematicLibrary) -> dict[SchematicComponentId, Schematic]:
    """
    Fetch the schematics of all components used in a schematic.
    """
    components: dict[SchematicComponentId, Schematic] = {}

    for component_id, component_schematic_id in schematic.components.items():
        component_schematic = library.get_schematic_or_none(component_schematic_id)
        if component_schematic is None:
            raise Exception(f"Schematic {component_schematic_id} required for {schematic.schematic_id} was not found in library.")
        components[component_id] = component_schematic

    return components

def get_input_connections_for_component(schematic: Schematic, component_id: SchematicComponentId | SchematicInput | SchematicOutput) -> list[Connection]:
    results = [
        connection
        for connection in schematic.connections
        if connection.destination.component == component_id
    ]
    return results

def get_output_connections_for_component(schematic: Schematic, component_id: SchematicComponentId | SchematicInput | SchematicOutput) -> list[Connection]:
    results = [
        connection
        for connection in schematic.connections
        if connection.source.component == component_id
    ]
    return results

def are_connections_resolved(schematic: Schematic, connections: list[Connection],  signal_state: dict[Connection, bool | None]) -> bool:
    return all (
        signal_state.get(connection) is not None
        for connection in connections
    )

# Test AND gate schematic
test_schematic = Schematic(
    schematic_id=SchematicId("AND"),
    input_pins=set( [PinId("in1"), PinId("in2")] ),
    output_pins=set( [PinId("out")] ),
    components={
        # nand1 -> NAND
        SchematicComponentId("nand1"): SchematicId("NAND"),
        # nand2 -> NAND
        SchematicComponentId("nand2"): SchematicId("NAND"),
    },
    connections = set([
        # input.in1 -> nand1.in1
        Connection(
            source = OutputAttachmentPoint(
                component = SchematicInput(),
                pin = OutputPinId("in1")
            ),
            destination = InputAttachmentPoint(
                component = SchematicComponentId("nand1"),
                pin = InputPinId("in1")
            )
        ),

        # input.in2 -> nand2.in1
        Connection(
            source = OutputAttachmentPoint(
                component = SchematicInput(),
                pin = OutputPinId("in2")
            ),
            destination = InputAttachmentPoint(
                component = SchematicComponentId("nand1"),
                pin = InputPinId("in2")
            )
        ),

        # nand1.out -> nand2.in1
        Connection(
            source = OutputAttachmentPoint(
                component = SchematicComponentId("nand1"),
                pin = OutputPinId("out")
            ),
            destination = InputAttachmentPoint(
                component = SchematicComponentId("nand2"),
                pin = InputPinId("in1")
            )
        ),

        # nand1.out -> nand2.in2
        Connection(
            source = OutputAttachmentPoint(
                component = SchematicComponentId("nand1"),
                pin = OutputPinId("out")
            ),
            destination = InputAttachmentPoint(
                component = SchematicComponentId("nand2"),
                pin = InputPinId("in2")
            )
        ),

        # nand2.out -> output.out
        Connection(
            source = OutputAttachmentPoint(
                component = SchematicComponentId("nand2"),
                pin = OutputPinId("out")
            ),
            destination = InputAttachmentPoint(
                component = SchematicOutput(),
                pin = InputPinId("out")
            )
        ),
    ])
)


if __name__ == "__main__":
    library = SchematicLibrary()
    library.add_schematic(test_schematic)

    results = library.simulate_schematic(
        test_schematic, 
        {
            OutputPinId("in1"): True,
            OutputPinId("in2"): True 
        }
    )

    print(results)
