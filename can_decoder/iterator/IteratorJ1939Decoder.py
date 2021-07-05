from datetime import datetime, timezone
from typing import Iterable, List, Optional

import numpy as np

from can_decoder.iterator.IteratorDecoder import IteratorDecoder
from can_decoder.Signal import Signal
from can_decoder.SignalDB import SignalDB
from can_decoder.support import is_valid_j1939_signal


class IteratorJ1939Decoder(IteratorDecoder):
    def __init__(self, wrapped: Iterable, conversion_rules: SignalDB, *args, **kwargs):
        super(IteratorJ1939Decoder, self).__init__(wrapped=wrapped, conversion_rules=conversion_rules)

        # Map the DBC file for quicker lookups on PGNs.
        self._frames = {}

        for frame_id, frame in self._db.frames.items():
            pgn = (frame_id & 0x03FFFF00) >> 8
    
            self._frames[pgn] = frame
        return
    
    @classmethod
    def get_supported_protocols(cls) -> List[Optional[str]]:
        return ["J1939"]

    def _decode_multiplexed(self, can_id: int, frame_data: np.ndarray, index: datetime, multiplexer: Signal):
        # Find corresponding muxer values.
        demultiplexed_ids = self._decode_signal_raw(multiplexer, frame_data)
    
        # Bundle these into unique IDs.
        unique_multiplexed_ids = np.unique(demultiplexed_ids)
    
        # Find signals for each id.
        for unique_id in unique_multiplexed_ids:
            indices = np.where(demultiplexed_ids == unique_id)[0]
            signals = multiplexer.signals.get(unique_id, [])
        
            signal_data = frame_data[indices, :]
        
            for signal in signals:
                if signal.is_multiplexer:
                    # Recursive decoding.
                    self._decode_multiplexed(
                        can_id=can_id,
                        frame_data=signal_data,
                        index=index,
                        multiplexer=signal
                    )
                else:
                    # No more multiplexing, decode.
                    self._decode(
                        signal=signal,
                        signal_data=signal_data,
                        time_stamp=index,
                        signal_id=can_id
                    )
            
                pass
        return

    def _decode(self, signal, signal_data, time_stamp, signal_id):
        signal_data_raw = self._decode_signal_raw(signal, signal_data)
    
        # Ensure the signal is valid.
        if signal_data_raw.size == 0 or not is_valid_j1939_signal(signal_data_raw[0], signal):
            return
    
        signal_data = self._decode_signal_raw_to_phys(signal, signal_data_raw)
    
        self._add_data(
            index=time_stamp,
            can_id=signal_id,
            data_raw=signal_data_raw[0, 0],
            data_physical=signal_data[0, 0],
            signal=signal
        )
        
        return
    
    def _get_data(self, data) -> None:
        # If this is not an extended frame, skip.
        if not data.IDE:
            return
        
        raw_id = np.uint32(data.ID) | np.uint32(0x80000000)
        
        # Create PGN.
        pgn = (raw_id & 0x03FFFF00) >> 8

        pgn_f = (pgn & 0xFF00) >> 8
        pgn_s = pgn & 0x00FF

        if pgn_f < 240:
            pgn &= 0xFFFFFF00
        
        # Locate supported frame.
        frame = self._frames.get(pgn, None)
    
        if frame is None:
            # Frame not supported, skip.
            return
        
        # Extract the raw data and the timestamp.
        frame_data = np.array([list(data.DataBytes)], dtype=np.uint8)
        time_stamp = datetime.utcfromtimestamp(data.TimeStamp * 1E-9).replace(tzinfo=timezone.utc)

        for signal in frame.signals:
            if signal.is_multiplexer:
                # Recursive decoding.
                self._decode_multiplexed(
                    can_id=raw_id,
                    frame_data=frame_data,
                    index=time_stamp,
                    multiplexer=signal
                )
            else:
                self._decode(
                    signal=signal,
                    signal_data=frame_data,
                    time_stamp=time_stamp,
                    signal_id=raw_id
                )
            pass
        
        return
    
    pass
