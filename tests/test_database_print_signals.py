import pytest

import can_decoder


@pytest.mark.env("canmatrix")
class TestSignalDBPrintSignals(object):

    def test_print_with_multiplex(self):
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
    
        result = str(db)
        
        expected_str = """SignalDB with 1 frames
	CAN Frame with ID 0x000007E8 - 8 bytes and 1 direct signals
		Signal "ServiceMux" 8:8 multiplex for 1 group(s):
			Group with ID 65 and 1 signal(s):
				Signal "PIDMux" 16:8 multiplex for 1 group(s):
					Group with ID 12 and 1 signal(s):
						Signal "EngineRPM" 24:16"""
        
        assert result == expected_str
        
        return

    pass
