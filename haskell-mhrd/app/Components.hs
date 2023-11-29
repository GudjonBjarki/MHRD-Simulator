module Components where

newtype ComponentId = ComponentId String deriving (Show, Eq)

newtype PinId = PinId String deriving (Show, Eq)

newtype InputPin = InputPin PinId deriving (Show, Eq)
newtype OutputPin = OutputPin PinId deriving (Show, Eq)

data CircuitInput = CircuitInput deriving (Show, Eq)
data CircuitOutput = CircuitOutput deriving (Show, Eq)

data InputConnectionPoint = InputConnectionPoint
  { inputComponentId :: Either ComponentId CircuitOutput
  , pin :: InputPin
  } deriving (Show, Eq)

data OutputConnectionPoint = OutputConnectionPoint
  { outputComponentId :: Either ComponentId CircuitInput
  , outputpin :: OutputPin
  } deriving (Show, Eq)


data Connection = Connection
  { source :: OutputConnectionPoint
  , destination :: InputConnectionPoint
  } deriving (Show, Eq)

newtype ComponentType = ComponentType String deriving (Show, Eq)


data Component = Component
  { componentType :: ComponentType
  , inputPins :: [InputPin]
  , outputPins :: [OutputPin]
  , components :: [(ComponentId, ComponentType)]
  , connections :: [Connection]
  } deriving (Show, Eq)

type ComponentLibrary = [Component]

type PinState = (OutputConnectionPoint, Bool)
type CircuitState = [PinState]


-- Barebones implementation of NAND gate since logic is hardcoded.
nandGate :: Component
nandGate = Component
  { componentType = ComponentType "NAND"
  , inputPins = [InputPin (PinId "in1"), InputPin (PinId "in2")]
  , outputPins = [OutputPin (PinId "out")]
  , components = []
  , connections = []
  }

evalComponent :: ComponentLibrary -> Component -> [(PinId, Bool)] -> [(PinId, Bool)]

evalComponent _ (Component {componentType = ComponentType "NAND"}) [(PinId "in1", a), (PinId "in2", b)] = [(PinId "out", not (a && b))]
evalComponent _ (Component {componentType = ComponentType "NAND"}) _ = error "Incorrect NAND input pins"

evalComponent library component inputs =
    if not $ validateSignals (inputPins component) inputs
      then error "Incorrect input pins"
      else undefined

validateSignals :: [InputPin] -> [(PinId, Bool)] -> Bool
validateSignals expectedPins inputSignals = allInputsPresent && noExtraInputs
  where
    expectedPinIds = map (\(InputPin pinId) -> pinId) expectedPins
    signalPinIds = map fst inputSignals
    allInputsPresent = all (`elem` signalPinIds) expectedPinIds
    noExtraInputs = all (`elem` expectedPinIds) signalPinIds

