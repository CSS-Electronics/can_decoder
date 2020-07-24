from typing import Dict

import canmatrix

from os import PathLike

from can_decoder.Frame import Frame
from can_decoder.Signal import Signal
from can_decoder.SignalDB import SignalDB


def load_dbc(dbc_file: PathLike, *args, **kwargs):
    """From a DBC file, load a set of frames and signals for conversion.
    
    :param dbc_file:    Path to a DBC file.
    :param args:        Additional args.
    :param kwargs:      Additional keywords.
    :return:            SignalDB with the loaded rules.
    """
    result = None
    
    # If a custom attribute is requested, determine the name here.
    use_custom_attribute = kwargs.get("use_custom_attribute", None)
    
    # Load the file using canmatrix.
    with open(dbc_file, "rb") as handle:
        dbc = canmatrix.formats.load_flat(handle, "dbc")
        
    # Create a new DB instance.
    result = SignalDB(protocol=dbc.attribute("ProtocolType", None))
    
    # Copy over all the signals.
    for dbc_frame in dbc:
        frame = Frame(
            frame_id=dbc_frame.arbitration_id.to_compound_integer(),
            frame_size=dbc_frame.size
        )
        
        # Extract all relevant signals.
        multiplexed = {}
        
        all_signals = []
        
        for dbc_signal in dbc_frame.signals:
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
            
            if use_custom_attribute is not None:
                # Attempt to use a custom attribute as input.
                signal.name = dbc_signal.attributes.get(use_custom_attribute, signal.name)
            
            if len(dbc_signal.mux_val_grp) != 0:
                # Find the corresponding multiplexer group.
                mux_group = multiplexed.get(dbc_signal.muxer_for_signal, None)
                
                if mux_group is None:
                    mux_group = {}
                    multiplexed[dbc_signal.muxer_for_signal] = mux_group
                
                mux_group[dbc_signal.mux_val] = signal

            if dbc_signal.muxer_for_signal is None:
                # This is a root signal.
                frame.signals.append(signal)
            
            all_signals.append(signal)
            pass
        
        # Iterate over all the frame signals for multiplexers.
        if len(multiplexed) != 0:
            multiplexer_names = list(multiplexed.keys())
            
            # If a signals contains the name of a multiplexer, it must be a child.
            for multiplexer_name in multiplexer_names:
                # Find the corresponding signal.
                multiplexer_signal = None

                for signal in all_signals:
                    if signal.name == multiplexer_name:
                        multiplexer_signal = signal
                        break
                
                if multiplexer_signal is None:
                    raise RuntimeError("Could not find multiplexor")
                
                # Find all depending signals.
                multiplexer_signal.signals = multiplexed[multiplexer_name]
                
                pass

            pass
        
        # Store in DB.
        result.frames[frame.id] = frame
    
    return result
