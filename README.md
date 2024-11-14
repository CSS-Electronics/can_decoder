# CAN Decoder - DBC decode CAN Data [LEGACY]
This package lets you DBC decode raw CAN data from the [CANedge](https://www.csselectronics.com/) to human-readable form (physical values) in Python.

## Update: Legacy notice + new Python integration methods
If you need to work with the CANedge data in Python, we now recommend to use the methods described in the below documentation:
- CANedge + Python: [About](https://www.csselectronics.com/pages/python-can-bus-api) | [Intro](https://canlogger.csselectronics.com/canedge-getting-started/ce3/log-file-tools/api-tools)

The Python modules `mdf-iter`, `canedge-browser` and `can-decoder` are now considered legacy. We instead refer to our new integration with python-can - and our examples of how to work with DBC decoded Parquet data lakes in Python using our MF4 decoders. For details see the links above.


---
### Key features
```
1. Easily decode raw CAN bus data via DBC files
2. Support for regular CAN, OBD2 and J1939
3. Very fast data conversion and minimal external dependencies
4. Output to pandas dataframe for easy use of the data
5. Conversion can be done iteratively (from iterator) or in bulk (from DataFrame) 
6. Can be used together with our mdf_iter and canedge_browser
```

---
### Installation
Use pip to install the `can_decoder` module:
```
pip install can_decoder
```
Optionally install `canmatrix` and `pandas` to load DBC files and enable conversion of pandas dataframes:
```
pip install canmatrix pandas
```

---
### Dependencies
* `numpy` (required)
* `canmatrix` (optional)
* `pandas` (optional)

---
### Module usage example
Below we load a log file via `mdf_iter` and use `can_decoder` to DBC decode it:
```
import can_decoder
import mdf_iter

mdf_path = "00000001.MF4"
dbc_path = "j1939.dbc"

db = can_decoder.load_dbc(dbc_path)
df_decoder = can_decoder.DataFrameDecoder(db)

with open(mdf_path, "rb") as handle:
    mdf_file = mdf_iter.MdfFile(handle)
    df_raw = mdf_file.get_data_frame()

df_phys = df_decoder.decode_frame(df_raw)
print(df_phys)
```

Further examples are included in the repo.

---
### Documentation
#### Supplying decoding rules
Data decoding is based on a set of signals which can be grouped together in frames. The frames in turn are grouped together in a single database. The list of rules can be crafted by hand, using the primitives `Signal`, `Frame` and `SignalDB` - or generated from a DBC file.

##### From a DBC file
If `canmatrix` is installed, the library can load the conversion rules from a DBC file:
```
db = can_decoder.load_dbc(dbc_path)
```
By default, the output will distinguish signals by the signal name (e.g. EngineSpeed). It is possible to switch from the primary signal name to another signal attribute in the DBC file by supplying the optional `use_custom_attribute` keyword. This takes the form of a string, and can e.g. be used to select SPNs instead of signal names in a J1939 DBC file. If no valid attribute is found, the signal name is used instead.
```
db = can_decoder.load_dbc(dbc_path, use_custom_attribute="SPN")
```

#### Data conversion
The library supports two methods of decoding data:
* Iteratively
* Bulk

##### Data conversion (iterator)
For iterative decoding (frame-by-frame), the library uses the `IteratorDecoder` class. This class takes a set of conversion rules (e.g. from a DBC file) and an iterable object (e.g. a MDF file):

```
decoder = can_decoder.IteratorDecoder(mdf_file, db)

for record in decoder:
    ...
```

This method expects an iterator structure like that of `mdf_iter` - incl. the following fields:
* `ID` - integer specifying the 11 or 29 bit CAN ID
* `IDE` - boolean specifying if the record uses a regular 11 bit ID or an extended 29 bit ID
* `DataBytes` - A bytearray, in the order the data bytes appear on the CAN bus.
* `TimeStamp` - A floating point number, representing seconds passed since epoch

In the case multiple signals are defined from a single ID, the library iterator will queue them internally, deferring the request for more data until all signals have been consumed from the iterator.

The output is of the form `decoded_signal`, which is a `namedtuple` with the following fields:
* `TimeStamp` - timestamp of the record as regular Python datetime
* `CanID` - CAN ID from the sending frame
* `Signal` - name of the decoded signal
* `SignalValueRaw` - raw value of the decoded signal
* `SignalValuePhysical` - physical value of the decoded signal

#### Data conversion (DataFrame)
For batch conversion of messages, the library uses the `DataFrameDecoder` class. This is constructed with the conversion rules as a parameter and can be re-used several times from the same set of parameters:

```
df_decoder = can_decoder.DataFrameDecoder(db)

df_phys_1 = df_decoder.decode_frame(df_raw_1)
df_phys_2 = df_decoder.decode_frame(df_raw_2)
```

The data supplied should be similar to that of the iterator method, but as a DataFrame. See also the initial example. Unlike the iterator component, this method does not require the presence of a time stamp entry. Instead, the index of the DataFrame passed to the decoder will be used as the index in the resulting DataFrame.

The output is a dataframe with the same index as the input dataframe, containing decoded results for the frames matched by the loaded DBC file. 

##### DataFrame output columns
The available signals in the output depends on the type of conversion. For generic CAN data (incl. OBD2), the following output columns are included:

* `CAN ID` - CAN ID of the frame, with the extended flag set as the most significant bit
* `Signal` - signal name string
* `Raw Value` - the raw value used as input in the decoding
* `Physical Value` - the physical value (after scaling and offset correction)

When decoding data using a J1939 DBC, the output includes the following extra columns:
* `PGN` - the PGN of the CAN frame
* `Source Address` - the source of the data
* `Signal` - the signal name

To remove columns from the output you can use the keyword `columns_to_drop`:
```
df_phys = df_decoder.decode_frame(df_raw, columns_to_drop=["CAN ID", "Raw Value"])
```
