"""
Collection of simple wrapper types.
"""

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

class InputPinId(PinId):
    """
    An identifier used to define an output pin on a schematic.
    A single output pin can have multiple or no connections from it.
    """
    pass

class SchematicInput:
    """
    @TODO: Document
    """
    pass

class SchematicOutput:
    """
    @TODO: Document
    """
    pass


class InputAttachmentPoint:
    """
    A point on a schematic where a connection can be created to.
    """
    component: SchematicComponentId | SchematicOutput
    pin: InputPinId

class OutputAttachmentPoint:
    """
    A point on a schematic where a connection can be created from.
    """
    component: SchematicComponentId | SchematicInput
    pin: OutputPin

class Connection:
    """
    A connection between and OutputAttachmentPoint and an InputAttachmentPoint.
    The signal outputed from the OutputAttachmentPoint will be propagated to the InputAttachmentPoint.
    """
    source: OutputAttachmentPoint
    destination: InputAttachmentPoint


