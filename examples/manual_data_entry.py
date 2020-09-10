import can_decoder

import pandas as pd

from datetime import datetime, timedelta, timezone


def setup_db_j1939() -> can_decoder.SignalDB:
    """Helper function to setup example decoding rules for J1939.
    
    :return: Database with example J1939 decoding rules.
    """
    # Special decoding rules are required for J1939, so specify the protocol.
    db = can_decoder.SignalDB(protocol="J1939")
    
    frame = can_decoder.Frame(
        frame_id=0x0CF00401,
        frame_size=8
    )
    
    signal_a = can_decoder.Signal(
        signal_name="EngineSpeed",
        signal_offset=0,
        signal_start_bit=32,
        signal_size=16,
        signal_factor=0.125,
        signal_is_little_endian=True,
        signal_is_float=False,
        signal_is_signed=False,
    )
    
    frame.add_signal(signal_a)
    
    db.add_frame(frame)
    
    return db


def setup_db_obd2() -> can_decoder.SignalDB:
    """Helper function to setup example decoding rules for OBD2.

    :return: Database with example OBD2 decoding rules.
    """
    # While not required for correct decoding, OBD2 is specified as the protocol type.
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


def example_manual_j1939():
    """Manually enter a few frames as a list and decode using J1939 rules.
    """
    timestamp = datetime.now(timezone.utc)

    frames = [
        {
            "TimeStamp": timestamp.timestamp() * 1E9,
            "ID": 0x0CF004FE,
            "IDE": True,
            "DataBytes": [
                0x10, 0x7D, 0x82, 0xBD, 0x12, 0x00, 0xF4, 0x82
            ]
        },
        {
            "TimeStamp": timestamp.timestamp() * 1E9 + 1E6,
            "ID": 0x0CF004FE,
            "IDE": True,
            "DataBytes": [
                0x10, 0x7D, 0x82, 0xBD, 0x1A, 0x00, 0xF4, 0x82
            ]
        },
        {
            "TimeStamp": timestamp.timestamp() * 1E9 + 2E6,
            "ID": 0x0CF004FE,
            "IDE": True,
            "DataBytes": [
                0x10, 0x7D, 0x82, 0xBD, 0x22, 0x00, 0xF4, 0x82
            ]
        }
    ]
    
    result = can_decoder.IteratorDecoder(frames, setup_db_j1939())
    for r in result:
        print(r)
    
    return


def example_manual_obd2():
    """Manually enter a few frames as a dataframe and decode using OBD2 rules.
    """
    timestamp = datetime.now(timezone.utc)
    
    frames = [
        {
            "TimeStamp": timestamp,
            "ID": 0x07E8,
            "IDE": False,
            "DataBytes": [
                0x04, 0x41, 0x0C, 0x32, 0x32, 0xAA, 0xAA, 0xAA
            ]
        },
        {
            "TimeStamp": timestamp + timedelta(milliseconds=1),
            "ID": 0x07E8,
            "IDE": False,
            "DataBytes": [
                0x04, 0x41, 0x0C, 0x32, 0x3A, 0xAA, 0xAA, 0xAA
            ]
        },
        {
            "TimeStamp": timestamp + timedelta(milliseconds=2),
            "ID": 0x07E8,
            "IDE": False,
            "DataBytes": [
                0x04, 0x41, 0x0C, 0x32, 0x42, 0xAA, 0xAA, 0xAA
            ]
        }
    ]

    test_data = pd.DataFrame(frames).set_index("TimeStamp")
    
    decoder = can_decoder.DataFrameDecoder(setup_db_obd2())
    result = decoder.decode_frame(test_data)
    
    print(result)
    
    return


if __name__ == '__main__':
    example_manual_j1939()
    example_manual_obd2()
    pass
