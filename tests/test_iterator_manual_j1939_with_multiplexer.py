from datetime import datetime, timezone
from random import randint

import pytest
import can_decoder

from tests.FillType import FillType


class TestIteratorManualJ1939(object):
    
    @pytest.fixture()
    def db_j1939(self):
        # Setup decoding rules.
        # NOTE: This is just re-using the ODB2 rules, but marking the DB as using J1939 rules.
        db = can_decoder.SignalDB(protocol="J1939")
        
        frame = can_decoder.Frame(
            frame_id=0x8CF004FE,
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
    
    @pytest.mark.parametrize(
        ("with_fill",),
        [(FillType.FillType_NONE,), (FillType.FillType_OBD2,), (FillType.FillType_RANDOM,)]
    )
    def test_single_valid_data(self, db_j1939, with_fill: FillType):
        # Create a list with a single frame of correct data.
        timestamp = datetime.now(timezone.utc)
        id = 0x8CF004FE
        ide = True
        data_bytes = [
            0x04, 0x41, 0x0C, 0x32, 0x32
        ]
        signal_name = "EngineRPM"
        signal_value_raw = 12850
        signal_value_scaled = 12850.25
        
        missing_byte_count = 8 - len(data_bytes)
        if with_fill == FillType.FillType_RANDOM:
            for i in range(missing_byte_count):
                data_bytes.append(randint(0, 255))
        elif with_fill == FillType.FillType_OBD2:
            for i in range(missing_byte_count):
                data_bytes.append(0xAA)
        elif with_fill == FillType.FillType_NONE:
            pass
        
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
                CanID=id,
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
                "ID": 0x8CF004FE,
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
    
    def test_no_matching_rule(self, db_j1939):
        # Create a list with a single frame of incorrect data (Missing a byte).
        frames = [
            {
                "TimeStamp": datetime.now(timezone.utc).timestamp(),
                "ID": 0x8CF004FE,
                "IDE": True,
                "DataBytes": [
                    0x01, 0x23
                ]
            }
        ]
        
        # Setup UUT.
        uut = can_decoder.IteratorDecoder(frames, db_j1939)
        
        result = list(uut)
        
        assert len(result) == 0, "Expected no matching rules"
        
        return
    
    pass
