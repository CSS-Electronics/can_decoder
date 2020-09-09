from collections import namedtuple


can_record = namedtuple(
    "CANRecord", [
        "TimeStamp",
        "ID",
        "IDE",
        "DataBytes",
    ]
)
