import queue

from abc import abstractmethod, ABCMeta
from datetime import datetime
from typing import Iterable

from can_decoder.DecoderBase import DecoderBase
from can_decoder.Signal import Signal
from can_decoder.SignalDB import SignalDB
from can_decoder.iterator.decoded_signal import decoded_signal


class IteratorDecoder(DecoderBase, metaclass=ABCMeta):
    def __new__(cls, wrapped: Iterable, conversion_rules: SignalDB, *args, **kwargs):
        # Examine the protocol field.
        dbc_protocol = conversion_rules.protocol
    
        # Locate a matching decoder for this protocol.
        decoder_map = {}
    
        for sub_class in IteratorDecoder.__subclasses__():  # type: IteratorDecoder
            supported_protocols = sub_class.get_supported_protocols()
        
            for protocol in supported_protocols:
                decoder_map[protocol] = sub_class
    
        # Attempt to find the corresponding decoder in the map.
        result = decoder_map.get(dbc_protocol, None)
    
        if result is None:
            # Try to get a generic decoder.
            result = decoder_map.get(None, None)
    
        if result is None:
            raise ValueError("No known support for protocol: \"{}\"".format(dbc_protocol))
    
        return super(IteratorDecoder, cls).__new__(result)
    
    def __init__(self, wrapped: Iterable, conversion_rules: SignalDB):
        super().__init__(conversion_rules=conversion_rules)
        
        self._wrapped = wrapped
        self._wrapped_iter = None

        self._signal_fifo = queue.Queue()
        return

    def __iter__(self) -> Iterable[decoded_signal]:
        self._wrapped_iter = self._wrapped.__iter__()
        return self
    
    @abstractmethod
    def _get_data(self, data):
        """
        
        :return:
        """
        raise NotImplementedError("")
    
    def _add_data(
            self,
            index: datetime,
            can_id: int,
            data_raw: float,
            data_physical: float,
            signal: Signal
    ):
        self._signal_fifo.put_nowait(
            decoded_signal(
                TimeStamp=index,
                CanID=can_id,
                SignalValueRaw=data_raw,
                SignalValuePhysical=data_physical,
                Signal=signal.name
            )
        )
        return
    
    def __next__(self) -> decoded_signal:
        while self._signal_fifo.empty():
            # Extract data from the wrapped iterator.
            data = self._wrapped_iter.__next__()
            
            self._get_data(data)
        
        return self._signal_fifo.get_nowait()
    
    pass





