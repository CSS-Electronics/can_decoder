from abc import abstractmethod, ABCMeta
from typing import List, Optional, Union

import numpy as np
import pandas as pd

from can_decoder.DecoderBase import DecoderBase
from can_decoder.Signal import Signal
from can_decoder.SignalDB import SignalDB


class DataFrameDecoder(DecoderBase, metaclass=ABCMeta):
    """Abstract baseclass for DataFrame conversion.
    
    This class overrides :code:`__new__` in order to dynamically select the correct implementation, based on the
    registered sub-classes. An implementation is supplied for the generic case, as well as for J1939. To register
    decoders for other protocols, inherit from this class and implement
    :py:meth:`can_decoder.DecoderBase.DecoderBase.get_supported_protocols`.
    """
    def __new__(cls, conversion_rules: SignalDB, *args, **kwargs):
        # Examine the protocol field.
        dbc_protocol = conversion_rules.protocol
        
        # Locate a matching decoder for this protocol.
        decoder_map = {}
        
        for sub_class in DataFrameDecoder.__subclasses__():  # type: DataFrameDecoder
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
        
        return super(DataFrameDecoder, cls).__new__(result)
    
    def __init__(self, conversion_rules: SignalDB):
        """Create a new decoder using the supplied rules.
        
        :param conversion_rules:    Rules to utilize when doing conversions.
        """
        super().__init__(conversion_rules=conversion_rules)
        
        self._common_time_base = False
        self._columns_to_drop = set([])
        self._result = []  # type: List[pd.DataFrame]
        return

    @classmethod
    def _get_fused_ids(cls, df: pd.DataFrame) -> np.ndarray:
        """To simplify operations, merge the ID and IDE columns into a single entity. The most significant bit is set to
        the IDE value.
        
        For instance, a non-extended CAN ID of :code:`0x7FF` would become :code:`0x000007FF`, while the extended pendent
        would be :code:`0x800007FF`.
        
        Expects the DataFrame to contain a column withs CAN IDs named **ID** and a column with the extended ID flag named
        **IDE**.
        
        :param df:  Dataframe containing ID and IDE data.
        :return:    Array of uint32, where the lowest 29 bits contain the CAN ID, and the highest bit contain the IDE
                    flag.
        """
        # Determine if it is possible to fuse the ID and IDE columns together.
        id_column = df.get("ID")  # type: Optional[pd.Series]
        ide_column = df.get("IDE")  # type: Optional[pd.Series]
        
        if ide_column is None:
            raise RuntimeError("Missing column")

        result = ide_column.to_numpy(dtype=np.uint32, copy=True)
        result <<= 31
        result |= id_column.array
        
        return result
    
    def _add_series(self, df: pd.DataFrame) -> None:
        """Collect the partial results.
        
        This simplifies the export mechanism, since multiple representations can be handled.
        
        :param df:      Signal DataFrame with all fields.
        """
        
        # Determine which fields to show, and drop the remaining.
        columns_in_frame = set(df.columns)
        columns_to_drop_in_frame = self._columns_to_drop.intersection(columns_in_frame)
        
        self._result.append(df.drop(columns=columns_to_drop_in_frame))
        
        return
    
    def decode_frame(self, df: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:
        """Decode a dataframe in bulk using the loaded rules.
        
        Expected columns in the dataframe:
        
        * **ID** - Containing the 29 bit CAN ID as an unsigned integer
        * **IDE** - Containing the extended ID bit as a boolean
        * **DataBytes** - A Python list of integers, where each integer has the value of the corresponding byte in the
          payload. Expects the first byte in the list to be the first byte on the wire.
        
        :param df: Dataframe to decode
        :return: Dataframe 
        """
        # Validate input data.
        columns = df.columns.values
        
        if "ID" not in columns:
            raise ValueError("Missing ID column in input data")
        elif "IDE" not in columns:
            raise ValueError("Missing IDE column in input data")
        elif "DataBytes" not in columns:
            raise ValueError("Missing DataBytes column in input data")
        
        # Read options. Determine which columns to drop.
        self._columns_to_drop = set(kwargs.get("columns_to_drop", []))
        
        # Handle output format.
        self._common_time_base = kwargs.pop("common_time_base", False)
        
        if self._common_time_base:
            self._result = pd.DataFrame(index=df.index)
        else:
            self._result = []
            
        # Delegate decoding to specialization.
        self._decode_frame(df, *args, **kwargs)

        if len(self._result) != 0:
            result = pd.concat(self._result)
            result = result.sort_index()
        else:
            result = pd.DataFrame()
        
        return result

    @abstractmethod
    def _decode_frame(self, df: pd.DataFrame, *args, **kwargs) -> None:
        """Specialization method called from the super-class, letting the sub-class handle the decoding.
        
        :param df:      DataFrame with the data. Format as expected by decode_frame.
        :param args:    Additional args as passed to the decode_frame function.
        :param kwargs:  Additional kwargs as passed to the decode_frame function.
        """
        raise NotImplementedError("")
    
    pass
