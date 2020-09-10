import pytest
import can_decoder
import ctypes

from datetime import datetime, timezone


class TempFrame(ctypes.LittleEndianStructure):
    _pack_ = 1
    _fields_ = [
        ('cj', ctypes.c_longlong, 8),
        ('hj1err', ctypes.c_longlong, 2),
        ('hj1tmp', ctypes.c_longlong, 12),
        ('hj2err', ctypes.c_longlong, 2),
        ('hj2tmp', ctypes.c_longlong, 12),
        ('hj3err', ctypes.c_longlong, 2),
        ('hj3tmp', ctypes.c_longlong, 12),
        ('hj4err', ctypes.c_longlong, 2),
        ('hj4tmp', ctypes.c_longlong, 12),
    ]


def int2twos(val, bits):  # pragma: no cover
    # Check if value fits in number of bits
    if val >= (1 << (bits - 1)):
        raise ValueError("Value too high")
    if val < (-1 * (1 << (bits - 1))):
        raise ValueError("Value too low")
    
    # To twos complement
    if val >= 0:
        return val & ~(1 << bits - 1)
    else:
        return (1 << bits - 1) + val | (1 << bits - 1)


class TestIteratorCustom(object):
    @pytest.fixture()
    def setup_db(self) -> can_decoder.SignalDB:
        # Create new DB with no protocol.
        db = can_decoder.SignalDB()
        
        # Add frame.
        frame = can_decoder.Frame(
            frame_id=0x80000001,
            frame_size=8
        )
        
        signal_cj_temp = can_decoder.Signal(
            signal_name="CJTemp",
            signal_start_bit=0,
            signal_size=8,
            signal_is_little_endian=True,
            signal_is_signed=True,
        )
        
        signal_hj1_temp = can_decoder.Signal(
            signal_name="HJ1Temp",
            signal_start_bit=10,
            signal_size=12,
            signal_is_little_endian=True,
            signal_is_signed=True,
        )
        
        signal_hj2_temp = can_decoder.Signal(
            signal_name="HJ2Temp",
            signal_start_bit=24,
            signal_size=12,
            signal_is_little_endian=True,
            signal_is_signed=True,
        )
        
        signal_hj3_temp = can_decoder.Signal(
            signal_name="HJ3Temp",
            signal_start_bit=38,
            signal_size=12,
            signal_is_little_endian=True,
            signal_is_signed=True,
        )
        
        signal_hj4_temp = can_decoder.Signal(
            signal_name="HJ4Temp",
            signal_start_bit=52,
            signal_size=12,
            signal_is_little_endian=True,
            signal_is_signed=True,
        )
        
        signal_hj1_err = can_decoder.Signal(
            signal_name="HJ1Err",
            signal_start_bit=8,
            signal_size=2,
            signal_is_signed=False,
        )
        
        signal_hj2_err = can_decoder.Signal(
            signal_name="HJ2Err",
            signal_start_bit=22,
            signal_size=2,
            signal_is_signed=False,
        )
        
        signal_hj3_err = can_decoder.Signal(
            signal_name="HJ3Err",
            signal_start_bit=36,
            signal_size=2,
            signal_is_signed=False,
        )
        
        signal_hj4_err = can_decoder.Signal(
            signal_name="HJ4Err",
            signal_start_bit=50,
            signal_size=2,
            signal_is_signed=False,
        )
        
        frame.add_signal(signal_cj_temp)
        frame.add_signal(signal_hj1_temp)
        frame.add_signal(signal_hj1_err)
        frame.add_signal(signal_hj2_temp)
        frame.add_signal(signal_hj2_err)
        frame.add_signal(signal_hj3_temp)
        frame.add_signal(signal_hj3_err)
        frame.add_signal(signal_hj4_temp)
        frame.add_signal(signal_hj4_err)
        db.add_frame(frame)
        
        return db
    
    @pytest.fixture()
    def setup_data(self) -> [dict]:
        payloads = []
        payloads.append(
            TempFrame(cj=int2twos(25, 8), hj1err=0, hj1tmp=int2twos(1, 12), hj2err=1, hj2tmp=int2twos(10, 12), hj3err=2,
                      hj3tmp=int2twos(100, 12), hj4err=3, hj4tmp=int2twos(1000, 12)))
        payloads.append(
            TempFrame(cj=int2twos(-25, 8), hj1err=0, hj1tmp=int2twos(-1, 12), hj2err=1, hj2tmp=int2twos(-10, 12),
                      hj3err=2, hj3tmp=int2twos(-100, 12), hj4err=3, hj4tmp=int2twos(-1000, 12)))
        
        # Create frames
        frames = []
        for i, payload in enumerate(payloads):
            frames.append({"TimeStamp": datetime(2000, 1, 1, 0, 0, i, 0).replace(tzinfo=timezone.utc).timestamp() * 1E9, "ID": 0x1, "IDE": True,
                           "DataBytes": list(bytes(payload))})
        
        return frames
    
    def test_custom_valid(self, setup_db, setup_data):
        # Setup conversion rules.
        conversion_rules = setup_db
        
        # Setup test data.
        test_data = setup_data
        
        # Setup expected result.
        expected = [
            can_decoder.DecodedSignal(TimeStamp=datetime(2000, 1, 1, 0, 0).replace(tzinfo=timezone.utc), CanID=0x80000001, Signal='CJTemp',
                                      SignalValueRaw=25, SignalValuePhysical=25.0),
            can_decoder.DecodedSignal(TimeStamp=datetime(2000, 1, 1, 0, 0).replace(tzinfo=timezone.utc), CanID=0x80000001, Signal='HJ1Temp',
                                      SignalValueRaw=1, SignalValuePhysical=1.0),
            can_decoder.DecodedSignal(TimeStamp=datetime(2000, 1, 1, 0, 0).replace(tzinfo=timezone.utc), CanID=0x80000001, Signal='HJ1Err',
                                      SignalValueRaw=0, SignalValuePhysical=0.0),
            can_decoder.DecodedSignal(TimeStamp=datetime(2000, 1, 1, 0, 0).replace(tzinfo=timezone.utc), CanID=0x80000001, Signal='HJ2Temp',
                                      SignalValueRaw=10, SignalValuePhysical=10.0),
            can_decoder.DecodedSignal(TimeStamp=datetime(2000, 1, 1, 0, 0).replace(tzinfo=timezone.utc), CanID=0x80000001, Signal='HJ2Err',
                                      SignalValueRaw=1, SignalValuePhysical=1.0),
            can_decoder.DecodedSignal(TimeStamp=datetime(2000, 1, 1, 0, 0).replace(tzinfo=timezone.utc), CanID=0x80000001, Signal='HJ3Temp',
                                      SignalValueRaw=100, SignalValuePhysical=100.0),
            can_decoder.DecodedSignal(TimeStamp=datetime(2000, 1, 1, 0, 0).replace(tzinfo=timezone.utc), CanID=0x80000001, Signal='HJ3Err',
                                      SignalValueRaw=2, SignalValuePhysical=2.0),
            can_decoder.DecodedSignal(TimeStamp=datetime(2000, 1, 1, 0, 0).replace(tzinfo=timezone.utc), CanID=0x80000001, Signal='HJ4Temp',
                                      SignalValueRaw=1000, SignalValuePhysical=1000.0),
            can_decoder.DecodedSignal(TimeStamp=datetime(2000, 1, 1, 0, 0).replace(tzinfo=timezone.utc), CanID=0x80000001, Signal='HJ4Err',
                                      SignalValueRaw=3, SignalValuePhysical=3.0),
            can_decoder.DecodedSignal(TimeStamp=datetime(2000, 1, 1, 0, 0, 1).replace(tzinfo=timezone.utc), CanID=0x80000001, Signal='CJTemp',
                                      SignalValueRaw=231, SignalValuePhysical=-25.0),
            can_decoder.DecodedSignal(TimeStamp=datetime(2000, 1, 1, 0, 0, 1).replace(tzinfo=timezone.utc), CanID=0x80000001, Signal='HJ1Temp',
                                      SignalValueRaw=65535, SignalValuePhysical=-1.0),
            can_decoder.DecodedSignal(TimeStamp=datetime(2000, 1, 1, 0, 0, 1).replace(tzinfo=timezone.utc), CanID=0x80000001, Signal='HJ1Err',
                                      SignalValueRaw=0, SignalValuePhysical=0.0),
            can_decoder.DecodedSignal(TimeStamp=datetime(2000, 1, 1, 0, 0, 1).replace(tzinfo=timezone.utc), CanID=0x80000001, Signal='HJ2Temp',
                                      SignalValueRaw=65526, SignalValuePhysical=-10.0),
            can_decoder.DecodedSignal(TimeStamp=datetime(2000, 1, 1, 0, 0, 1).replace(tzinfo=timezone.utc), CanID=0x80000001, Signal='HJ2Err',
                                      SignalValueRaw=1, SignalValuePhysical=1.0),
            can_decoder.DecodedSignal(TimeStamp=datetime(2000, 1, 1, 0, 0, 1).replace(tzinfo=timezone.utc), CanID=0x80000001, Signal='HJ3Temp',
                                      SignalValueRaw=65436, SignalValuePhysical=-100.0),
            can_decoder.DecodedSignal(TimeStamp=datetime(2000, 1, 1, 0, 0, 1).replace(tzinfo=timezone.utc), CanID=0x80000001, Signal='HJ3Err',
                                      SignalValueRaw=2, SignalValuePhysical=2.0),
            can_decoder.DecodedSignal(TimeStamp=datetime(2000, 1, 1, 0, 0, 1).replace(tzinfo=timezone.utc), CanID=0x80000001, Signal='HJ4Temp',
                                      SignalValueRaw=64536, SignalValuePhysical=-1000.0),
            can_decoder.DecodedSignal(TimeStamp=datetime(2000, 1, 1, 0, 0, 1).replace(tzinfo=timezone.utc), CanID=0x80000001, Signal='HJ4Err',
                                      SignalValueRaw=3, SignalValuePhysical=3.0),
        ]
        
        # Test.
        uut = can_decoder.IteratorDecoder(test_data, conversion_rules=conversion_rules)
        
        result = list(uut)
        
        assert expected == result
    
    pass
