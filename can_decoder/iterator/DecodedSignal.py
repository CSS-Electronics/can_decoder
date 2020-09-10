from collections import namedtuple
from datetime import timedelta


_decoded_signal_named_tuple = namedtuple(
    "DecodedSignal", [
        "TimeStamp",
        "CanID",
        "Signal",
        "SignalValueRaw",
        "SignalValuePhysical",
    ]
)


class DecodedSignal(_decoded_signal_named_tuple):
    def __eq__(self, other):
        if (self.TimeStamp - other.TimeStamp) != timedelta(0):
            return False
        
        if self.CanID != other.CanID:
            return False
        
        if self.Signal != other.Signal:
            return False
        
        if self.SignalValueRaw != other.SignalValueRaw:
            return False
        
        if self.SignalValuePhysical != other.SignalValuePhysical:
            return False
        
        return True
    
    def __ne__(self, other):
        return not (self == other)
    
    pass
