from abc import ABCMeta, abstractmethod
from typing import List, Optional

import numpy as np

from can_decoder.Signal import Signal
from can_decoder.SignalDB import SignalDB


class DecoderBase(object, metaclass=ABCMeta):
    def __init__(self, conversion_rules: SignalDB):
        self._db = conversion_rules
        return
    
    @classmethod
    @abstractmethod
    def get_supported_protocols(cls) -> List[Optional[str]]:
        """Return a list of supported protocols.

        The library has implementations covering the generic case (None) and "J1939".

        :return:    List of supported protocols.
        """
        raise NotImplementedError("")

    @classmethod
    def _extract_signal_bits(cls, signal: Signal, data: np.ndarray) -> np.ndarray:
        """Given a signal description and an array of data bytes, extract the bits relevant for a signal. Result is
        returned as an array of signal data bytes. Handles endian changes.

        :param signal:  Signal to extract data for.
        :param data:    Array of data as uint8 bytes.
        :return:        Array of signal data as uint8 bytes, in little endian format.
        """
        # Determine the start and stop bits.
        start_bit = signal.start_bit
        stop_bit = signal.start_bit + signal.size
    
        # Extract the bytes relevant for the signal.
        start_byte = start_bit // 8
        stop_byte = stop_bit // 8
    
        if stop_bit % 8 != 0:
            stop_byte += 1
    
        reduced_data = data[:, start_byte:stop_byte]
    
        # Determine how to read the data depending on the endianness.
        if signal.is_little_endian:
            reduced_data_bits = np.unpackbits(reduced_data, axis=1, bitorder="little")
        else:
            reduced_data_bits = np.unpackbits(reduced_data, axis=1, bitorder="big")
    
        # Extract the signal bits, ignoring the surrounding data.
        subbyte_start_position = start_bit % 8
        bit_data_trail = reduced_data_bits[:, subbyte_start_position:subbyte_start_position + signal.size]
    
        # If the signal is in big endian, flip the bits to have a little endian representation.
        if not signal.is_little_endian:
            bit_data_trail = np.fliplr(bit_data_trail)
    
        # Repackage as bytes, in little endian orientation.
        packed = np.packbits(bit_data_trail, axis=1, bitorder="little")
    
        return packed

    @classmethod
    def _decode_signal_raw(cls, signal: Signal, data: np.ndarray) -> np.ndarray:
        """Given a signal and frame data, extract the raw value of the signal.

        :param signal:  Signal to extract.
        :param data:    Frame data as an array of uint8 bytes.
        :return:        Array of raw signal values, in the smallest possible dtype.
        """
    
        # Extract only the bits relevant for this signal.
        signal_data = cls._extract_signal_bits(signal, data)
    
        # Interpret as a single value instead of an array.
        signal_size_in_bytes = signal.size // 8
        if signal.size % 8 != 0:
            signal_size_in_bytes += 1
    
        # Construct the corresponding unsigned datatype.
        signal_single_datatype = "<u{}".format(signal_size_in_bytes)
    
        if len(signal_data.shape) == 0:
            # Frames with one dimension are simple to handle.
            new_shape = signal_data.shape[0]
        elif signal_size_in_bytes in (3, 5, 6, 7):
            # Handle frames of size 3, 5, 6 and 7 (We have access to single-, dual-, quad- and octo-byte
            # representations).
            next_size = 4 * (signal_size_in_bytes // 4 + 1)
            signal_single_datatype = "<u{}".format(next_size)
        
            # Create a new array since additional data is needed to fit in the next datatype.
            expanded_data = np.empty((signal_data.shape[0], next_size), dtype=np.uint8)
        
            # Copy the signal data into the LSB bytes.
            expanded_data[:, :signal_size_in_bytes] = signal_data
        
            # Set the remainder to zero.
            expanded_data[:, signal_size_in_bytes:] = 0
        
            signal_data = expanded_data
            new_shape = next_size * data.shape[0]
        else:
            new_shape = signal_size_in_bytes * data.shape[0]
    
        # Reshape to a single dimension.
        reshaped_data = signal_data.reshape(new_shape)
    
        # Interpret as single datatype.
        data_return = reshaped_data.view(dtype=signal_single_datatype)
    
        return data_return

    @classmethod
    def _decode_signal_raw_to_phys(cls, signal: Signal, data: np.ndarray) -> np.ndarray:
        """Given a signal and the raw data for the signal, extract the physical values.

        :param signal:  Signal to parse.
        :param data:    Raw data as an array of unsigned bytes.
        :return:        Array of decoded data.
        """
        if signal.is_float:
            # data = cls._handle_float_signal(signal, data)
            raise RuntimeError("Float not yet supported")
        else:
            data = cls._handle_integer_signal(signal, data)
    
        # Handle scaling to physical values if necessary.
        if signal.factor != 1:
            data = data * signal.factor
    
        # Correct for any offsets if necessary.
        if signal.offset != 0:
            data = data + signal.offset
    
        return data.astype(float)

    @staticmethod
    def _handle_float_signal(signal: Signal, data: np.ndarray) -> np.ndarray:
        if signal.size == 32:
            result = data.view(dtype=np.float32)
        elif signal.size == 64:
            result = data.view(dtype=np.float64)
        else:
            raise RuntimeError("Signal should be decoded as float, but is not 32 or 64 bits wide")
    
        # Convert to float.
        result = result.astype(dtype=np.float64)
    
        return result

    @staticmethod
    def _handle_integer_signal(signal: Signal, data: np.ndarray) -> np.ndarray:
        # If the data is signed, move the sign.
        if signal.is_signed:
            # Create mask targeting the MSB in the signal.
            mask_msb_detect = data.dtype.type(2 ** (signal.size - 1))
            mask_signal_select = data.dtype.type(2 ** signal.size - 1)
        
            # Get the indices where the signal is set.
            signed_bit_indices = np.where(data & mask_msb_detect)[0]
        
            # Set all bits above the signal MSB to 1.
            msb_mask = data.dtype.type(np.iinfo(data.dtype.type).max) & ~mask_signal_select
        
            # Update the places with the sign bit set.
            data[signed_bit_indices] = data[signed_bit_indices] | msb_mask
        
            # Switch the datatype from unsigned to signed.
            signed_datatype = np.dtype("<i{}".format(data.dtype.itemsize))
        
            result = data.view(dtype=signed_datatype)
        else:
            result = data
    
        return result
    
    pass
