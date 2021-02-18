from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from can_decoder.dataframe.DataFrameDecoder import DataFrameDecoder
from can_decoder.Frame import Frame
from can_decoder.Signal import Signal
from can_decoder.SignalDB import SignalDB


class DataFrameGenericDecoder(DataFrameDecoder):
    def __init__(self, conversion_rules: SignalDB):
        super(DataFrameGenericDecoder, self).__init__(conversion_rules=conversion_rules)
        pass

    @classmethod
    def get_supported_protocols(cls) -> List[Optional[str]]:
        return [None]
    
    def _decode_multiplexed(
            self,
            frame_data: np.ndarray,
            frame_ids: np.ndarray,
            index: pd.Index,
            multiplexer: Signal
    ):
        """Decode a multiplexed signal. Will recurse on itself if necessary.
        
        :param frame_data:
        :param frame_ids:
        :param index:
        :param multiplexer:
        """
        # Find corresponding multiplexer values.
        demultiplexed_ids = self._decode_signal_raw(multiplexer, frame_data)
        
        # Bundle these into unique IDs.
        unique_multiplexed_ids = np.unique(demultiplexed_ids)
        
        # Find signals for each ID.
        for unique_id in unique_multiplexed_ids:
            indices = np.where(demultiplexed_ids == unique_id)[0]
            signals = multiplexer.signals.get(unique_id, [])
            
            # Shared variables amongs all signals for this ID.
            signal_data = frame_data[indices, :]
            signal_index = index[indices]
            signal_ids = frame_ids[indices]
            
            for signal in signals:
                if signal.is_multiplexer:
                    # Recursive decoding.
                    self._decode_multiplexed(
                        frame_data=signal_data,
                        frame_ids=signal_ids,
                        index=signal_index,
                        multiplexer=signal
                    )
                else:
                    # No more multiplexing, decode.
                    self._decode(
                        signal=signal,
                        signal_data=signal_data,
                        signal_index=signal_index,
                        signal_ids=signal_ids
                    )
    
                pass
        
        return
    
    def _decode(self, signal, signal_data, signal_index, signal_ids):
        signal_data_raw = self._decode_signal_raw(signal, signal_data)
        
        if signal_data_raw.size == 0:
            return
        
        signal_data = self._decode_signal_raw_to_phys(signal, signal_data_raw)
    
        # Create a resulting series.
        signal_result = pd.DataFrame(index=signal_index)
        signal_result["CAN ID"] = signal_ids & 0x1FFFFFFF
        signal_result["Signal"] = signal.name
        signal_result["Raw Value"] = signal_data_raw
        signal_result["Physical Value"] = signal_data

        self._add_series(signal_result)
        
        return
    
    def _decode_frame(self, df: pd.DataFrame, *args, **kwargs):
        # Find all unique IDs. Use a combination of the 29 bit ID and the 1 bit IDE in 1 field.
        raw_ids = self._get_fused_ids(df)
        unique_ids = np.unique(raw_ids)
        
        # Find all supported frames.
        supported_ids = {}  # type: Dict[int, Frame]
        
        for unique_id in unique_ids:
            frame = self._db.frames.get(unique_id, None)
            
            if frame is not None:
                supported_ids[unique_id] = frame
        
        for unique_id, frame in supported_ids.items():
            # Determine which data indices to use.
            id_indices = np.where(raw_ids == unique_id)[0]
            
            data_lists = df["DataBytes"].values[id_indices]
            
            # Extract data.
            frame_data = np.array([a for a in data_lists], dtype=np.uint8)
            frame_ids = raw_ids[id_indices]

            # Extract the timestamps for index purposes.
            frame_index = df.index[id_indices]

            for signal in frame.signals:
                if signal.is_multiplexer:
                    # Recursive decoding.
                    self._decode_multiplexed(
                        frame_data=frame_data,
                        frame_ids=frame_ids,
                        index=frame_index,
                        multiplexer=signal
                    )
                else:
                    self._decode(
                        signal=signal,
                        signal_data=frame_data,
                        signal_ids=frame_ids,
                        signal_index=frame_index
                    )
                pass
        
        return
    
    pass
