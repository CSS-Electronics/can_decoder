from can_decoder.Signal import Signal


def get_j1939_limit(number_of_bits: int) -> int:
    """For a given signal length in bits, return the lowest invalid value, if the data was represented as an unsigned
    integer.
    
    :param number_of_bits:  The length of the J1939 signal in bits.
    :return:                The lowest possible value containing valid data.
    """
    limit = 0
    
    if number_of_bits == 2:
        limit = 0x3
    elif number_of_bits == 4:
        limit = 0xF
    elif number_of_bits == 8:
        limit = 0xFF
    elif number_of_bits == 10:
        limit = 0x3FF
    elif number_of_bits == 12:
        limit = 0xFF0
    elif number_of_bits == 16:
        limit = 0xFF00
    elif number_of_bits == 20:
        limit = 0xFF000
    elif number_of_bits == 24:
        limit = 0xFF0000
    elif number_of_bits == 28:
        limit = 0xFF00000
    elif number_of_bits == 32:
        limit = 0xFF000000
    else:
        limit = 0xFFFFFFFFFFFFFFFF
    
    return limit


def is_valid_j1939_signal(raw_value: int, signal: Signal) -> bool:
    """Given a raw J1939 signal value and the signal length in bits, determine if the signal is valid,
    
    :param raw_value:       The raw J1939 signal value.
    :param signal:  The length of the J1939 signal in bits.
    :return:                True if signal is in the valid region, False otherwise.
    """
    if signal.is_signed:
        # Early exit for signed signals.
        return True
    
    limit = get_j1939_limit(signal.size)
    
    if raw_value >= limit:
        result = False
    else:
        result = True
    
    return result
