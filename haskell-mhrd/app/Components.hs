module Components where

newtype ComponentId = ComponentId String deriving (Eq, Show)

newtype PartId = PartId String deriving (Eq, Show)

newtype PinId = PinId String deriving (Eq, Show)

data PartIoId = InputPin | OutputPin deriving (Eq, Show)

data PartIdOrIoId = PartIdWrapper PartId | PartIoIdWrapper PartIoId deriving (Eq, Show)

data PartPin = PartPin  { part  :: PartIdOrIoId
                        , pin   :: PinId } deriving (Eq, Show)

data Connection = Connection { from :: PartPin
                             , to  ::  PartPin } deriving (Eq, Show)

data Component = Component  { id :: ComponentId
                            , inputPins :: [PinId]
                            , outputPins :: [PinId]
                            , parts :: [(PartId, ComponentId)]
                            , connections :: [Connection] } deriving (Eq, Show)


