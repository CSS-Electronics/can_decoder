from collections import defaultdict
from typing import Optional

from can_decoder.Frame import Frame


class SignalDB(object):
    _protocol = None  # type: Optional[str]
    frames = defaultdict()
    
    def __init__(self, protocol: Optional[str] = None):
        """Create a new signal database, with a pre-defined protocol.
        
        :param protocol: Protocol to associate with the database.
        """
        self._protocol = protocol
        pass
    
    @property
    def protocol(self) -> Optional[str]:
        """Returns the protocol string of the signal database.
        
        :return: The current protocol string of the database.
        """
        return self._protocol
    
    def add_frame(self, frame: Frame) -> bool:
        """Add a CAN frame to the signal database.
        
        :return: True for frame successfully added, False otherwise.
        """
        if frame.id not in self.frames.keys():
            self.frames[frame.id] = frame
            return True
        
        return False
    
    pass
