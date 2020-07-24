import can_decoder


def setup_fs():
    """Helper function to setup the file system for the examples.
    """
    from fsspec.implementations.local import LocalFileSystem
    
    fs = LocalFileSystem()
    
    return fs


def decode_using_rules(handle, db):
    """Helper function to decode a single MDF file using the supplied rules.
    
    :param handle:  A file-like object already opened.
    :param db:      A SignalDB representing the decoding rules.
    :return:        A pandas DataFrame with the decoded results.
    """
    import mdf_iter
    
    # Create decoder.
    dataframe_decoder = can_decoder.DataFrameDecoder(db)
    
    # Open the file and extract a dataframe with the raw CAN records.
    mdf_file = mdf_iter.MdfFile(handle)
    
    df = mdf_file.get_data_frame()
    
    # Decode the dataframe in a bulk operation.
    decoded_result = dataframe_decoder.decode_frame(df)
    
    return decoded_result


def example_setup_decoding_rules_j1939():
    """Example of manually specifying the decoding rules, instead of supplying a DBC file.
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
    
    # Setup filesystem and which log file to decode.
    fs = setup_fs()
    device = "LOG/EEEE0005"
    log_file = "{}/00000001/00000001.MF4".format(device)
    
    with fs.open(log_file, "rb") as handle:
        decoded_result = decode_using_rules(handle, db)
    
    print(decoded_result)
    
    return


def example_setup_decoding_rules_obd2():
    """Example of manually specifying the decoding rules, instead of supplying a DBC file.
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

    # Setup filesystem and which log file to decode.
    fs = setup_fs()
    device = "LOG/EEEE0005"
    log_file = "{}/00000001/00000001.MF4".format(device)

    with fs.open(log_file, "rb") as handle:
        decoded_result = decode_using_rules(handle, db)

    print(decoded_result)


if __name__ == '__main__':
    example_setup_decoding_rules_j1939()
    example_setup_decoding_rules_obd2()
    pass
