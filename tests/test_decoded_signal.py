import can_decoder
import copy

from datetime import datetime, timedelta, timezone


class TestDecodedSignal(object):
    def test_equal_objects(self):
        timestamp = datetime.now(timezone.utc)
        id = 0x07E8
        signal_name = "EngineRPM"
        signal_value_raw = 12850
        signal_value_scaled = 12850.25
        
        object_a = can_decoder.iterator.DecodedSignal(
            TimeStamp=timestamp,
            CanID=id,
            Signal=signal_name,
            SignalValueRaw=signal_value_raw,
            SignalValuePhysical=signal_value_scaled
        )

        object_b = can_decoder.iterator.DecodedSignal(
            TimeStamp=timestamp,
            CanID=id,
            Signal=signal_name,
            SignalValueRaw=signal_value_raw,
            SignalValuePhysical=signal_value_scaled
        )
        
        assert object_a == object_b

        return

    def test_equal_objects_on_value(self):
        timestamp = datetime.now(timezone.utc)
        id = 0x07E8
        signal_name = "EngineRPM"
        signal_value_raw = 12850
        signal_value_scaled = 12850.25
    
        object_a = can_decoder.iterator.DecodedSignal(
            TimeStamp=timestamp,
            CanID=id,
            Signal=signal_name,
            SignalValueRaw=signal_value_raw,
            SignalValuePhysical=signal_value_scaled
        )
    
        object_b = can_decoder.iterator.DecodedSignal(
            TimeStamp=copy.deepcopy(timestamp),
            CanID=copy.deepcopy(id),
            Signal=copy.deepcopy(signal_name),
            SignalValueRaw=copy.deepcopy(signal_value_raw),
            SignalValuePhysical=copy.deepcopy(signal_value_scaled)
        )
    
        assert object_a == object_b

        return

    def test_different_timestamp(self):
        timestamp = datetime.now(timezone.utc)
        id = 0x07E8
        signal_name = "EngineRPM"
        signal_value_raw = 12850
        signal_value_scaled = 12850.25
    
        object_a = can_decoder.iterator.DecodedSignal(
            TimeStamp=timestamp,
            CanID=id,
            Signal=signal_name,
            SignalValueRaw=signal_value_raw,
            SignalValuePhysical=signal_value_scaled
        )
    
        object_b = can_decoder.iterator.DecodedSignal(
            TimeStamp=timestamp + timedelta(microseconds=1),
            CanID=id,
            Signal=signal_name,
            SignalValueRaw=signal_value_raw,
            SignalValuePhysical=signal_value_scaled
        )
    
        assert object_a != object_b

        return

    def test_different_can_id(self):
        timestamp = datetime.now(timezone.utc)
        id = 0x07E8
        signal_name = "EngineRPM"
        signal_value_raw = 12850
        signal_value_scaled = 12850.25
    
        object_a = can_decoder.iterator.DecodedSignal(
            TimeStamp=timestamp,
            CanID=id,
            Signal=signal_name,
            SignalValueRaw=signal_value_raw,
            SignalValuePhysical=signal_value_scaled
        )
    
        object_b = can_decoder.iterator.DecodedSignal(
            TimeStamp=timestamp,
            CanID=id + 1,
            Signal=signal_name,
            SignalValueRaw=signal_value_raw,
            SignalValuePhysical=signal_value_scaled
        )
    
        assert object_a != object_b

        return

    def test_different_signal_name(self):
        timestamp = datetime.now(timezone.utc)
        id = 0x07E8
        signal_name = "EngineRPM"
        signal_value_raw = 12850
        signal_value_scaled = 12850.25

        object_a = can_decoder.iterator.DecodedSignal(
            TimeStamp=timestamp,
            CanID=id,
            Signal=signal_name,
            SignalValueRaw=signal_value_raw,
            SignalValuePhysical=signal_value_scaled
        )

        object_b = can_decoder.iterator.DecodedSignal(
            TimeStamp=timestamp,
            CanID=id,
            Signal="DifferentSignal",
            SignalValueRaw=signal_value_raw,
            SignalValuePhysical=signal_value_scaled
        )

        assert object_a != object_b
        
        return

    def test_different_raw_value(self):
        timestamp = datetime.now(timezone.utc)
        id = 0x07E8
        signal_name = "EngineRPM"
        signal_value_raw = 12850
        signal_value_scaled = 12850.25

        object_a = can_decoder.iterator.DecodedSignal(
            TimeStamp=timestamp,
            CanID=id,
            Signal=signal_name,
            SignalValueRaw=signal_value_raw,
            SignalValuePhysical=signal_value_scaled
        )

        object_b = can_decoder.iterator.DecodedSignal(
            TimeStamp=timestamp,
            CanID=id,
            Signal=signal_name,
            SignalValueRaw=signal_value_raw + 1,
            SignalValuePhysical=signal_value_scaled
        )

        assert object_a != object_b
        
        return

    def test_different_scaled_value(self):
        timestamp = datetime.now(timezone.utc)
        id = 0x07E8
        signal_name = "EngineRPM"
        signal_value_raw = 12850
        signal_value_scaled = 12850.25

        object_a = can_decoder.iterator.DecodedSignal(
            TimeStamp=timestamp,
            CanID=id,
            Signal=signal_name,
            SignalValueRaw=signal_value_raw,
            SignalValuePhysical=signal_value_scaled
        )

        object_b = can_decoder.iterator.DecodedSignal(
            TimeStamp=timestamp,
            CanID=id,
            Signal=signal_name,
            SignalValueRaw=signal_value_raw,
            SignalValuePhysical=signal_value_scaled + 0.0000001
        )

        assert object_a != object_b

        return
    
    pass
