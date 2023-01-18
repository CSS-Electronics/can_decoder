from typing import Optional, List

from can_decoder.Frame import Frame
from can_decoder.Signal import Signal


class SignalDB(object):
    def __init__(self, protocol: Optional[str] = None):
        """Create a new signal database, with a pre-defined protocol.
        
        :param protocol: Protocol to associate with the database.
        """
        self._protocol = protocol
        self.frames = {}
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
    
    def signals(self) -> List[str]:
        """Get a list of all signals in the database.
        
        :return: List of all signals as strings.
        """
        result = []
        
        def yield_signals(result_list: List[str], signal: Signal):
            result_list.append(signal.name)
            
            if signal.is_multiplexer:
                for multiplex in signal.signals.values():
                    for sub_signal in multiplex:
                        yield_signals(result_list=result_list, signal=sub_signal)
            return

        for frame in self.frames.values():
            for signal in frame.signals:
                yield_signals(result_list=result, signal=signal)
            
        return result
        
    def get_frame_by_name(self, name: str) -> Frame:
      return next((frame for frame in self.frames.values() if frame.name == name), None)
      
    def __str__(self):
        # Generate a pretty nested tree.
        result = f"SignalDB with {len(self.frames)} frames"

        for frame in self.frames.values():
            frame_str = str(frame)
            
            for line in frame_str.splitlines():
                result += f"\n\t{line}"

        return result
    
    pass
