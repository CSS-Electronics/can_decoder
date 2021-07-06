import canmatrix

from os import PathLike
from typing import Union, BinaryIO, Sequence, Optional

from can_decoder.Frame import Frame
from can_decoder.Signal import Signal
from can_decoder.SignalDB import SignalDB


def load_dbc(dbc_file: Union[str, PathLike, BinaryIO], *args, **kwargs) -> Optional[SignalDB]:
    loader = DBCLoader()
    return loader.load_dbc(dbc_file=dbc_file, *args, **kwargs)


class DBCLoader(object):
    def __init__(self):
        self._use_custom_attribute = None
        return
    
    def load_dbc(self, dbc_file: Union[str, PathLike, BinaryIO], *args, **kwargs) -> Optional[SignalDB]:
        """From a DBC file, load a set of frames and signals for conversion.

        :param dbc_file:    Path to a DBC file.
        :param args:        Additional args.
        :param kwargs:      Additional keywords.
        :return:            SignalDB with the loaded rules.
        """
        result = None
    
        # If a custom attribute is requested, determine the name here.
        self._use_custom_attribute = kwargs.get("use_custom_attribute", None)
    
        # Attempt to determine the type of the input. Check for file-like first, attempt to use as a path second.
        if all(hasattr(dbc_file, attr) for attr in ("seek", "read", "readline")):
            dbc = canmatrix.formats.load_flat(dbc_file, "dbc")
        else:
            with open(dbc_file, "rb") as handle:
                dbc = canmatrix.formats.load_flat(handle, "dbc")
    
        # Create a new DB instance.
        result = SignalDB(protocol=dbc.attribute("ProtocolType", None))
    
        # Load all frames.
        for dbc_frame in dbc:
            frame = self._load_frame(dbc_frame=dbc_frame)
            
            if frame is not None:
                result.add_frame(frame=frame)
            
            # Store in DB.
            result.add_frame(frame)
    
        return result

    def _load_frame(self, dbc_frame: canmatrix.Frame) -> Frame:
        frame = Frame(
            frame_id=dbc_frame.arbitration_id.to_compound_integer(),
            frame_size=dbc_frame.size
        )
    
        # Loop over all signals, load multiplexed signals using special handler (And thus ignore them in
        # the loading loop).
        for dbc_signal in dbc_frame.signals:
            if dbc_signal.is_multiplexer and dbc_signal.mux_val is None:
                # Multiplexer, but is not self multiplexed. Check complexity.
                if dbc_frame.is_complex_multiplexed is True:
                    signal = self._multiplexed_signal_loader_complex(
                        muxer_signal=dbc_signal,
                        dbc_signals=dbc_frame.signals
                    )
                else:
                    signal = self._multiplexed_signal_loader_simple(
                        muxer_signal=dbc_signal,
                        dbc_signals=dbc_frame.signals
                    )
                    
                frame.add_signal(signal)
            elif not dbc_signal.is_multiplexer and dbc_signal.mux_val is None:
                # Not a multiplexer and not a multiplexed signal.
                frame.add_signal(self._signal_loader(dbc_signal=dbc_signal))
            pass
    
        return frame

    def _multiplexed_signal_loader_complex(self, muxer_signal: canmatrix.Signal, dbc_signals: Sequence[canmatrix.Signal]) -> Signal:
        # Convert root signal.
        multiplexed_signal = self._signal_loader(muxer_signal)
    
        # Locate all signals this is multiplexing for.
        for signal in dbc_signals:
            if signal == muxer_signal:
                continue
            
            if signal.muxer_for_signal == muxer_signal.name:
                if signal.is_multiplexer:
                    # Nested loading required, as this is a multiplexer for another signal.
                    multiplexed_signal.add_multiplexed_signal(
                        signal.mux_val,
                        self._multiplexed_signal_loader_complex(signal, dbc_signals)
                    )
                else:
                    # Plain signal, use as normal.
                    multiplexed_signal.add_multiplexed_signal(
                        signal.mux_val,
                        self._signal_loader(signal)
                    )
                    pass
                pass
            pass
    
        return multiplexed_signal

    def _multiplexed_signal_loader_simple(self, muxer_signal: canmatrix.Signal, dbc_signals: Sequence[canmatrix.Signal]) -> Signal:
        # Convert root signal.
        multiplexed_signal = self._signal_loader(muxer_signal)
    
        # Locate all signals this is multiplexing for.
        for signal in dbc_signals:
            if signal == muxer_signal:
                continue
                
            if signal.is_multiplexer:
                # Nested loading required, as this is a multiplexer for another signal.
                multiplexed_signal.add_multiplexed_signal(
                    signal.mux_val,
                    self._multiplexed_signal_loader_simple(signal, dbc_signals)
                )
            else:
                # Plain signal, use as normal.
                multiplexed_signal.add_multiplexed_signal(
                    signal.mux_val,
                    self._signal_loader(signal)
                )
                pass
            pass
    
        return multiplexed_signal

    def _signal_loader(self, dbc_signal: canmatrix.Signal) -> Signal:
        signal = Signal(
            signal_name=dbc_signal.name,
            signal_start_bit=dbc_signal.start_bit,
            signal_size=dbc_signal.size,
            signal_is_float=dbc_signal.is_float,
            signal_is_signed=dbc_signal.is_signed,
            signal_is_little_endian=dbc_signal.is_little_endian,
            signal_factor=dbc_signal.factor,
            signal_offset=dbc_signal.offset
        )

        if self._use_custom_attribute is not None:
            # Attempt to use a custom attribute as input.
            signal.name = dbc_signal.attributes.get(self._use_custom_attribute, signal.name)
    
        return signal

    pass
