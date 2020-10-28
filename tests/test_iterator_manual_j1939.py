from datetime import datetime, timezone

import pytest
import can_decoder


class TestIteratorManualJ1939(object):
    
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
    
    def test_single_valid_data(self, db_j1939):
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
        
        frames = [
            {
                "TimeStamp": timestamp.timestamp() * 1E9,
                "ID": id,
                "IDE": ide,
                "DataBytes": data_bytes
            }
        ]
        
        expected = [
            can_decoder.DecodedSignal(
                TimeStamp=timestamp,
                CanID=id | 0x80000000,
                Signal=signal_name,
                SignalValueRaw=signal_value_raw,
                SignalValuePhysical=signal_value_scaled
            )
        ]

        # Setup UUT.
        uut = can_decoder.IteratorDecoder(frames, db_j1939)
        
        result = list(uut)
        
        # Ensure the correct decoded signal is present in the result.
        assert result == expected
        
        return

    def test_invalid_data(self, db_j1939):
        # Create a list with a single frame of incorrect data (Missing a byte).
        frames = [
            {
                "TimeStamp": datetime.now(timezone.utc).timestamp(),
                "ID": 0x0CF004FE,
                "IDE": True,
                "DataBytes": [
                    0x04, 0x41, 0x0C, 0x32
                ]
            }
        ]
        
        # Setup UUT.
        uut = can_decoder.IteratorDecoder(frames, db_j1939)

        with pytest.warns(can_decoder.CANDecoderWarning):
            result = list(uut)

        assert len(result) == 0
    
        return
    
    pass
