from typing import Union, Dict


class Signal(object):
    name = ""  # type: str
    factor = 1  # type: Union[int, float]
    offset = 0  # type: Union[int, float]
    start_bit = 0  # type: int
    size = 0  # type: int
    is_little_endian = True  # type: bool
    is_signed = False  # type: bool
    is_float = False  # type: bool
    signals = None  # type: Dict[int, Signal]
    
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
        self.signals[id] = signal
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
    
    def __repr__(self) -> str:
        name = self.name
        
        if name == "":
            name = "Unnamed"
        
        return "Signal \"{}\" {}:{}".format(
            name,
            self.start_bit,
            self.size
        )

    def __hash__(self) -> int:
        return hash(self._get_tuple())

    def __eq__(self, other) -> bool:
        if not isinstance(other, Signal):
            return NotImplemented
    
        return self._get_tuple() == other._get_tuple()

    pass
