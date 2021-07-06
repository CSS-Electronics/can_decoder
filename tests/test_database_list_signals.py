import pytest

import can_decoder


@pytest.mark.env("canmatrix")
class TestSignalDBListSignals(object):

    def test_list_with_multiplex(self):
        # Setup decoding rules.
        db = can_decoder.SignalDB(protocol="OBD2")
    
        frame = can_decoder.Frame(
            frame_id=0x000007E8,
            frame_size=8
        )
    
        signal_main_mux = can_decoder.Signal(
            signal_name="ServiceMux",
            signal_start_bit=8,
            signal_size=8,
            signal_factor=1,
            signal_offset=0,
            signal_is_little_endian=False,
            signal_is_float=False,
            signal_is_signed=False,
        )
    
        signal_minor_mux = can_decoder.Signal(
            signal_name="PIDMux",
            signal_start_bit=16,
            signal_size=8,
            signal_factor=1,
            signal_offset=0,
            signal_is_little_endian=False,
            signal_is_float=False,
            signal_is_signed=False,
        )
    
        signal_engine = can_decoder.Signal(
            signal_name="EngineRPM",
            signal_start_bit=24,
            signal_size=16,
            signal_factor=1,
            signal_offset=0.25,
            signal_is_little_endian=False,
            signal_is_float=False,
            signal_is_signed=False,
        )
    
        # Link the signals and muxes.
        signal_minor_mux.add_multiplexed_signal(0x0C, signal_engine)
        signal_main_mux.add_multiplexed_signal(0x41, signal_minor_mux)
        frame.add_signal(signal_main_mux)
    
        db.add_frame(frame)
    
        result = db.signals()
        
        expected_signal_list = [
            signal_main_mux.name,
            signal_minor_mux.name,
            signal_engine.name
        ]
        
        assert set(expected_signal_list) == set(result)
        
        return

    pass
