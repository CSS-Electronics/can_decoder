from typing import Dict, List, Union


class Signal(object):
    name = ""  # type: str
    factor = 1  # type: Union[int, float]
    offset = 0  # type: Union[int, float]
    start_bit = 0  # type: int
    size = 0  # type: int
    is_little_endian = True  # type: bool
    is_signed = False  # type: bool
    is_float = False  # type: bool
    signals = None  # type: Dict[int, List[Signal]]
    
    def __init__(
            self,
            signal_name: str,
            signal_start_bit: int,
            signal_size: int,
            signal_is_little_endian: bool = True,
            signal_is_signed: bool = False,
            signal_is_float: bool = False,
            signal_factor: Union[int, float] = 1,
            signal_offset: Union[int, float] = 0
    ) -> None:
        self.name = signal_name
        self.factor = signal_factor
        self.offset = signal_offset
        self.start_bit = signal_start_bit
        self.size = signal_size
        self.is_little_endian = signal_is_little_endian
        self.is_signed = signal_is_signed
        self.is_float = signal_is_float
        self.signals = {}
    
    @property
    def is_multiplexer(self):
        return len(self.signals) != 0
    
    def add_multiplexed_signal(self, id, signal):
        mux_group = self.signals.get(id, None)
        
        if mux_group is None:
            mux_group = []
            self.signals[id] = mux_group
        
        mux_group.append(signal)
        return
    
    def _get_tuple(self):
        return (
            self.name,
            self.factor,
            self.offset,
            self.start_bit,
            self.size,
            self.is_little_endian,
            self.is_signed,
            self.is_float,
        )
    
    def __str__(self) -> str:
        name = self.name
        
        if name == "":
            name = "Unnamed"
        
        result = f"Signal \"{name}\" {self.start_bit}:{self.size}"
        
        if self.is_multiplexer:
            result += f" multiplex for {len(self.signals)} group(s):"
            
            for group_id, signals in self.signals.items():
                result += f"\n\tGroup with ID {group_id} and {len(signals)} signal(s):"
                
                for signal in signals:
                    signal_str = str(signal)

                    for line in signal_str.splitlines():
                        result += f"\n\t\t{line}"
                
        return result

    def __hash__(self) -> int:
        return hash(self._get_tuple())

    def __eq__(self, other) -> bool:
        if not isinstance(other, Signal):
            return NotImplemented
    
        return self._get_tuple() == other._get_tuple()

    pass
