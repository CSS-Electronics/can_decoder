from collections import namedtuple


decoded_signal = namedtuple(
    "DecodedSignal", [
        "TimeStamp",
        "CanID",
        "Signal",
        "SignalValueRaw",
        "SignalValuePhysical",
    ]
)
