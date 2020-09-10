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
    def db_j1939(self):
        # Setup decoding rules.
        db = can_decoder.SignalDB(protocol="J1939")
        
        frame = can_decoder.Frame(
            frame_id=0x8CF004FE,
            frame_size=8
        )
        
        signal_engine_speed = can_decoder.Signal(
            signal_name="EngineSpeed",
            signal_start_bit=24,
            signal_size=16,
            signal_factor=0.125,
            signal_offset=0,
            signal_is_little_endian=True,
            signal_is_float=False,
            signal_is_signed=False,
        )
        
        frame.add_signal(signal_engine_speed)
        
        db.add_frame(frame)
        
        return db
    
    @pytest.fixture()
    def uut(self, db_j1939):
        decoder = can_decoder.DataFrameDecoder(db_j1939)
        
        return decoder
    
    def test_single_valid_data(self, uut):
        # Create a list with a single frame of correct data.
        timestamp = datetime.now(timezone.utc)
        id = 0x0CF004FE
        ide = True
        data_bytes = [
            0x10, 0x7D, 0x82, 0xBD, 0x12, 0x00, 0xF4, 0x82
        ]
        signal_name = "EngineSpeed"
        signal_value_raw = 4797
        signal_value_scaled = 599.625
        signal_pgn = 0xF004
        signal_source_address = 0xFE
        
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
                "PGN": signal_pgn,
                "Source Address": signal_source_address,
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
        # Create a list with a single frame of correct data, but the only supported signal is out of range.
        timestamp = datetime.now(timezone.utc)
        id = 0x0CF004FE
        ide = True
        data_bytes = [
            0x10, 0x7D, 0x82, 0xBD, 0xFF, 0x00, 0xF4, 0x82
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
    
        result = uut.decode_frame(test_data)
    
        assert len(result) == 0
    
        return

    def test_missing_data(self, uut):
        # Create a list with a single frame of correct data.
        timestamp = datetime.now(timezone.utc)
        id = 0x0CF004FE
        ide = True
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
        
        with pytest.raises(can_decoder.CANDecoderException):
            uut.decode_frame(test_data)
        
        return
    
    pass
