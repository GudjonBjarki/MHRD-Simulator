"""
Collection of simple wrapper types.
"""
from dataclasses import dataclass

class SchematicId(str):
    """
    A unique identifier for a schematic stored in a schematic library.
    """
    pass

class SchematicComponentId(str):
    """
    An identifier for a component within a schematic.

    Example:
        This mhrd code 'nand1->NAND' defines a component within a schematic.
        The component has the SchematicComponentId('nand1') and the SchematicId('NAND')
    """
    pass

class PinId(str):
    """
    An identifier used to define a pin on a schematic.
    Typically PinId should only be used for type hinting.
    Use either InputPinId or OutputPinId when working on a schematic.
    """
    pass

class InputPinId(PinId):
    """
    An identifier used to define an input pin on a schematic.
    This pin must be provided only a single signal with a connection from a single OutputPin.
    """
    pass

class OutputPinId(PinId):
    """
    An identifier used to define an output pin on a schematic.
    A single output pin can have multiple or no connections from it.
    """
    pass

class SchematicInput:
    """
    @TODO: Document
    """
    def __eq__(self, other: object) -> bool:
        return isinstance(other, SchematicInput)
    
    def __hash__(self) -> int:
        return hash("SchematicInput")

class SchematicOutput:
    """
    @TODO: Document
    """
    def __eq__(self, other: object) -> bool:
        return isinstance(other, SchematicOutput)
    
    def __hash__(self) -> int:
        return hash("SchematicOutput")

@dataclass
class InputAttachmentPoint:
    """
    A point on a schematic where a connection can be created to.
    """
    component: SchematicComponentId | SchematicOutput
    pin: InputPinId

    def __hash__(self) -> int:
        return hash((self.component, self.pin))

@dataclass
class OutputAttachmentPoint:
    """
    A point on a schematic where a connection can be created from.
    """
    component: SchematicComponentId | SchematicInput
    pin: OutputPinId

    def __hash__(self) -> int:
        return hash((self.component, self.pin))

@dataclass
class Connection:
    """
    A connection between and OutputAttachmentPoint and an InputAttachmentPoint.
    The signal outputed from the OutputAttachmentPoint will be propagated to the InputAttachmentPoint.
    """
    source: OutputAttachmentPoint
    destination: InputAttachmentPoint

    def __hash__(self) -> int:
        return hash((self.source, self.destination))