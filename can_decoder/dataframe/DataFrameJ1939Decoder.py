import numpy as np
import pandas as pd
import warnings

from typing import List, Optional

from can_decoder.SignalDB import SignalDB
from can_decoder.support import get_j1939_limit
from can_decoder.dataframe.DataFrameDecoder import DataFrameDecoder
from can_decoder.warnings.DataSizeMismatchWarning import DataSizeMismatchWarning


class DataFrameJ1939Decoder(DataFrameDecoder):
    """Optimized method for decoding J1939 in bulk.

    Assumes that DLC always encodes for 8 bytes.
    """
    
    def __init__(self, conversion_rules: SignalDB):
        super(DataFrameJ1939Decoder, self).__init__(conversion_rules=conversion_rules)
        
        # Map the DBC file for quicker lookups on PGNs.
        self._frames = {}
        
        for frame_id, frame in self._db.frames.items():
            pgn = self._calculate_pgn(frame_id)
            self._frames[pgn] = frame
        
        return
    
    @staticmethod
    def _calculate_pgn(frame_id):
        pgn = (frame_id & 0x03FFFF00) >> 8
    
        pgn_f = (pgn & 0xFF00) >> 8
        pgn_s = pgn & 0x00FF
    
        if pgn_f < 240:
            pgn &= 0xFFFFFF00
        
        return pgn
    
    @classmethod
    def get_supported_protocols(cls) -> Optional[List[str]]:
        return ["J1939"]
    
    def _decode_frame_with_well_formed_data(self, reduced_df, frame, raw_ids, id_indices, *args, **kwargs):
        # Should invalid values be ignored? Defaults to true.
        ignore_invalid = kwargs.get("ignore_invalid_signals", True)

        data_lists = reduced_df["DataBytes"]
        index = reduced_df.index
        
        frame_data = np.array([a for a in data_lists], dtype=np.uint8)
        frame_ids = raw_ids[id_indices]
    
        # Decode each signal contained in this frame.
        for signal in frame.signals:
            # Get the raw representation.
            signal_data = self._decode_signal_raw(signal, frame_data)
        
            # Determine which measurements are invalid and need to be removed.
            valid_indices = np.array(range(0, len(signal_data)), dtype=np.uint64)
            if ignore_invalid:
                limit = get_j1939_limit(signal.size)
                valid_indices = np.argwhere(signal_data < limit)[:, 0]
        
            if valid_indices.shape[0] == 0:
                # Early skip if no valid data is located.
                continue
        
            # Create a new DataFrame to contain the results.
            result = pd.DataFrame(index=index[valid_indices])
        
            # Get raw and decoded data.
            signal_data_raw = signal_data[valid_indices]
            signal_data = self._decode_signal_raw_to_phys(signal, signal_data_raw)
        
            # Add custom fields.
            result["CAN ID"] = frame_ids[valid_indices] & 0x1FFFFFFF
            result["PGN"] = self._calculate_pgn(frame.id)
            result["Source Address"] = frame_ids[valid_indices] & np.uint32(0x000000FF)
            result["Signal"] = signal.name
            result["Raw Value"] = signal_data_raw
            result["Physical Value"] = signal_data
        
            self._add_series(result)
            
        return
    
    def _decode_frame(self, df: pd.DataFrame, *args, **kwargs):
        # Should invalid values be ignored? Defaults to true.
        ignore_invalid = kwargs.get("ignore_invalid_signals", True)
        
        # Find all unique IDs. Use a combination of the 29 bit ID and the 1 bit IDE in 1 field.
        raw_ids = self._get_fused_ids(df)
        
        # Remove any IDs which are not extended (Cannot be J1939 data).
        extended_ids = np.where(raw_ids & np.uint32(0x80000000))[0]
        
        raw_ids = raw_ids[extended_ids]
        raw_index = df.index[extended_ids]
        
        # Create a list of raw PGNs.
        raw_pgns = (raw_ids & np.uint32(0x00FF0000))
        
        pgn_indices = np.where(raw_pgns >= 0x00F00000)[0]
        
        raw_pgns[pgn_indices] |= raw_ids[pgn_indices] & np.uint32(0x0000FF00)
        raw_pgns |= raw_ids & np.uint32(0x03000000)
        
        raw_pgns >>= 8
        
        # Find a list of all unique PGNs.
        unique_pgns = np.unique(raw_pgns)
        
        # Extract and decode each PGN in turn.
        for pgn in unique_pgns:
            # Determine if this PGN is supported.
            frame = self._frames.get(pgn, None)
            
            if frame is None:
                # Can't decode this message, continue.
                continue
            
            # Extract the correct indices, and translate from the extended IDs to the full dataframe.
            id_indices = np.where(raw_pgns == pgn)[0]
            index = raw_index[id_indices]
            reduced_df = df.loc[index, :]
            
            try:
                self._decode_frame_with_well_formed_data(reduced_df, frame, raw_ids, id_indices)
            except ValueError as e:
                warnings.warn("Could not shape data for PGN {}".format(pgn), DataSizeMismatchWarning)
            
            pass
        
        return
    
    pass
