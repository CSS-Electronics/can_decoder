from enum import Enum, auto


class FillType(Enum):
    FillType_NONE = auto(),
    FillType_OBD2 = auto(),
    FillType_J1939 = auto(),
    FillType_RANDOM = auto(),
