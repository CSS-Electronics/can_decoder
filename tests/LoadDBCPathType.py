from enum import Enum, auto


class LoadDBCPathType(Enum):
    LoadDBCPathType_STR = auto(),
    LoadDBCPathType_PATH = auto(),
    LoadDBCPathType_FILE = auto(),
    LoadDBCPathType_MEMORY = auto(),
