from typing import List, Optional

from can_decoder.Signal import Signal


class Frame(object):
    id = 0  # type: int
    size = 0  # type: int
    signals = None  # type: List[Signal]
    multiplexer = None  # type: Optional[Signal]
    
    def __init__(
            self,
            frame_id: int,
            frame_size: int,
    ) -> None:
        self.id = frame_id
        self.size = frame_size
        self.signals = []
    
    def _get_tuple(self):
        return (
            self.id,
            self.size
        )
    
    def add_signal(self, *args, **kwargs) -> bool:
        """Add a new signal directly to this frame. All arguments are passed on the the Signal constructor.
        
        :param args:
        :param kwargs:
        :return:        True if signal added. False otherwise.
        """
        result = False
        
        # If only one argument is supplied, check if it already is a signal.
        if len(args) == 1:
            signal = args[0]
            if isinstance(signal, Signal):
                result = True
        else:
            try:
                signal = Signal(*args, **kwargs)
            except Exception:
                signal = None
                result = False
        
        if result:
            # Add the signal to the internal storage.
            self.signals.append(signal)
            
            # If the signal is a multiplexer, and no other signal is a multiplexer, set this as the root multiplexer.
            if self.multiplexer is None and signal.is_multiplexer:
                self.multiplexer = signal
            elif signal.is_multiplexer:
                raise ValueError(
                    """
Multiplexed signal added to frame, but frame already contains a root multiplexed signal.
Should the signal have been added to another signal as a multiplexed value?
                    """
                )
                pass
        
        return result
    
    def __repr__(self) -> str:
        return "CAN Frame with ID 0x{:08X} - {} bytes. {} registered signals".format(
            self.id,
            self.size,
            len(self.signals)
        )
    
    def __hash__(self) -> int:
        return hash(self._get_tuple())
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Frame):
            return NotImplemented
        
        return self._get_tuple() == other._get_tuple()
    
    pass
