from datetime import datetime, timezone

import can_decoder
import pytest

try:
    import pandas as pd
except ModuleNotFoundError:
    # Should be filtered by pytest when run with tox.
    pass


@pytest.mark.env("pandas")
class TestDataFrameManualOBD2(object):
    
    @pytest.fixture()
    def db_obd2(self):
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
        
        return db
    
    @pytest.fixture()
    def uut(self, db_obd2):
        decoder = can_decoder.DataFrameDecoder(db_obd2)
        
        return decoder
    
    def test_single_valid_data(self, uut):
        # Create a list with a single frame of correct data.
        timestamp = datetime.now(timezone.utc)
        id = 0x07E8
        ide = False
        data_bytes = [
            0x04, 0x41, 0x0C, 0x32, 0x32
        ]
        signal_name = "EngineRPM"
        signal_value_raw = 12850
        signal_value_scaled = 12850.25
        
        frames = [
            {
                "TimeStamp": timestamp,
                "ID": id,
                "IDE": ide,
                "DataBytes": data_bytes
            }
        ]

        test_data = pd.DataFrame(frames).set_index("TimeStamp")
        
        expected = [
            {
                "TimeStamp": timestamp,
                "CAN ID": id,
                "Signal": signal_name,
                "Raw Value": signal_value_raw,
                "Physical Value": signal_value_scaled
            }
        ]

        expected_data = pd.DataFrame(expected).set_index("TimeStamp")
        
        result = uut.decode_frame(test_data)

        # Set data types to the same as the result.
        expected_data = expected_data.astype(result.dtypes)

        # Ensure the correct decoded signal is present in the result.
        assert result.equals(expected_data)
        
        return

    def test_invalid_data(self, uut):
        # Create a list with a single frame of correct data.
        timestamp = datetime.now(timezone.utc)
        id = 0x07E8
        ide = False
        data_bytes = [
            0x04, 0x41, 0x0C, 0x32
        ]
    
        frames = [
            {
                "TimeStamp": timestamp,
                "ID": id,
                "IDE": ide,
                "DataBytes": data_bytes
            }
        ]
    
        test_data = pd.DataFrame(frames).set_index("TimeStamp")
        
        with pytest.warns(can_decoder.CANDecoderWarning):
            result = uut.decode_frame(test_data)
        
        assert result.size == 0
        
        return
    
    pass
