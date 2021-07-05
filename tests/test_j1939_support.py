import pytest
from can_decoder.Signal import Signal

from can_decoder.support import is_valid_j1939_signal


class TestJ1939Support(object):
    @pytest.mark.parametrize(
        ("value", "bits", "expected"),
        [
            (0b10, 2, True),
            (0b11, 2, False),
            (0b1110, 4, True),
            (0b1111, 4, False),
            (0xFE, 8, True),
            (0xFF, 8, False),
            (0x3FE, 10, True),
            (0x3FF, 10, False),
            (0xFEF, 12, True),
            (0xFF0, 12, False),
            (0xFEFF, 16, True),
            (0xFF00, 16, False),
            (0xFEFFF, 20, True),
            (0xFF000, 20, False),
            (0xFEFFFF, 24, True),
            (0xFF0000, 24, False),
            (0xFEFFFFF, 28, True),
            (0xFF00000, 28, False),
            (0xFEFFFFFF, 32, True),
            (0xFF000000, 32, False),
            (0x1FFFFFFFF, 33, True),
            (0x0000000000000000, 64, True),
            (0xFFFFFFFFFFFFFFFE, 64, True),
            (0xFFFFFFFFFFFFFFFF, 64, False),
        ]
    )
    def test_raw_signal_range(self, value: int, bits: int, expected: bool):
        signal = Signal(
            signal_name="test_signal",
            signal_start_bit=0,
            signal_size=bits
        )
        
        assert is_valid_j1939_signal(value, signal) == expected
        
        return
    
    pass
