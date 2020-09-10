from can_decoder.exceptions.CANDecoderException import CANDecoderException


class DataSizeMismatch(CANDecoderException):
    def __init__(self):
        super(DataSizeMismatch, self).__init__()
    
    pass
