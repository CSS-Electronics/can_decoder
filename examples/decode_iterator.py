import can_decoder
import mdf_iter

from pathlib import Path


def setup_fs():
    """Helper function to setup the file system for the examples.
    """
    from fsspec.implementations.local import LocalFileSystem
    
    fs = LocalFileSystem()
    
    return fs


def example_decode_using_iterator_j1939():
    """Example of loading a file and using the iterator to decode records as they are extracted.
    """
    
    # Specify path to the DBC file containing the decoding rules.
    dbc_path = Path(__file__).parent / "CSS-Electronics-SAE-J1939-DEMO.dbc"
    
    # Setup filesystem and which log file to decode.
    fs = setup_fs()
    device = "LOG/EEEE0005"
    log_file = "{}/00000001/00000001.MF4".format(device)
    
    # Import the decoding rules.
    db = can_decoder.load_dbc(dbc_path)
    
    with fs.open(log_file, "rb") as handle:
        # Open the file and extract an iterator for raw CAN records.
        mdf_file = mdf_iter.MdfFile(handle)
        
        raw_iterator = mdf_file.get_can_iterator()
        
        # Wrap the raw iterator with the decoder.
        wrapped_iterator = can_decoder.IteratorDecoder(raw_iterator, db)
    
        ctr = 0
        for signal in wrapped_iterator:
            print(signal)
            ctr += 1
    
        print("Found a total of {} decoded messages".format(ctr))
    
    return


def example_decode_using_iterator_obd2():
    """Example of loading a file and using the iterator to decode records as they are extracted.
    """
    
    # Specify path to the DBC file containing the decoding rules.
    dbc_path = Path(__file__).parent / "CSS-Electronics-OBD2-v1.3.dbc"
    
    # Setup filesystem and which log file to decode.
    fs = setup_fs()
    device = "LOG/EEEE0005"
    log_file = "{}/00000001/00000001.MF4".format(device)
    
    # Import the decoding rules.
    db = can_decoder.load_dbc(dbc_path)
    
    with fs.open(log_file, "rb") as handle:
        # Open the file and extract an iterator for raw CAN records.
        mdf_file = mdf_iter.MdfFile(handle)
        
        raw_iterator = mdf_file.get_can_iterator()
        
        # Wrap the raw iterator with the decoder.
        wrapped_iterator = can_decoder.IteratorDecoder(raw_iterator, db)
        
        ctr = 0
        for signal in wrapped_iterator:
            # The DBC file contains data for response type and length as well, which we skip.
            if signal.Signal in ["response", "length"]:
                continue
            print(signal)
            ctr += 1
        
        print("Found a total of {} decoded messages".format(ctr))
    
    return


if __name__ == '__main__':
    example_decode_using_iterator_j1939()
    example_decode_using_iterator_obd2()
    pass
