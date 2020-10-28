from can_decoder.exceptions import *
from can_decoder.iterator import IteratorDecoder, DecodedSignal
from can_decoder.warnings import *

from can_decoder.Frame import Frame
from can_decoder.Signal import Signal
from can_decoder.SignalDB import SignalDB

try:
    from can_decoder.dataframe import DataFrameDecoder
except ModuleNotFoundError:
    pass

try:
    import warnings

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        warnings.filterwarnings("ignore", category=SyntaxWarning)
        
        from can_decoder.DBCLoader import load_dbc
except ModuleNotFoundError:
    pass

from ._version import get_versions
__version__ = get_versions()["version"]
del get_versions
