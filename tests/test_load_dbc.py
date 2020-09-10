import pytest

from io import BytesIO
from pathlib import Path

import can_decoder
from tests.LoadDBCPathType import LoadDBCPathType


@pytest.mark.env("canmatrix")
class TestLoadDBC(object):

    @pytest.mark.parametrize(
        ("input_type",),
        [
            (LoadDBCPathType.LoadDBCPathType_STR, ),
            (LoadDBCPathType.LoadDBCPathType_PATH, ),
            (LoadDBCPathType.LoadDBCPathType_FILE, ),
            (LoadDBCPathType.LoadDBCPathType_MEMORY, )
        ]
    )
    def test_load_j1939_dbc(self, input_type: LoadDBCPathType):
        dbc_base_path = Path(__file__).parent.parent / "examples" / "CSS-Electronics-SAE-J1939-DEMO.dbc"

        if input_type == LoadDBCPathType.LoadDBCPathType_STR:
            result = can_decoder.load_dbc(str(dbc_base_path))
        elif input_type == LoadDBCPathType.LoadDBCPathType_PATH:
            result = can_decoder.load_dbc(dbc_base_path)
        elif input_type == LoadDBCPathType.LoadDBCPathType_FILE:
            with open(dbc_base_path, "rb") as handle:
                result = can_decoder.load_dbc(handle)
        elif input_type == LoadDBCPathType.LoadDBCPathType_MEMORY:
            with open(dbc_base_path, "rb") as handle:
                raw = handle.read()

            with BytesIO(raw) as handle:
                result = can_decoder.load_dbc(handle)

        # Ensure that a DB is loaded.
        assert result is not None, "Expected a DB to be loaded"

        # Ensure the protocol is set to J1939.
        assert result.protocol == "J1939", "Expected protocol to be J1939"

        # Ensure the correct signals are present.
        frame_ids = [0x8CF004FE, 0x98FEF1FE]
        assert len(result.frames) == len(frame_ids)

        frame_eec1 = result.frames[0x8CF004FE]  # type: can_decoder.Frame
        assert frame_eec1.id == 0x8CF004FE
        assert frame_eec1.multiplexer is None
        assert frame_eec1.size == 8
        assert len(frame_eec1.signals) == 1

        signal_engine_speed = frame_eec1.signals[0]
        assert signal_engine_speed.is_float is False
        assert signal_engine_speed.is_little_endian is True
        assert signal_engine_speed.is_multiplexer is False
        assert signal_engine_speed.is_signed is False
        assert signal_engine_speed.name == "EngineSpeed"
        assert signal_engine_speed.factor == 0.125
        assert signal_engine_speed.offset == 0
        assert signal_engine_speed.size == 16
        assert signal_engine_speed.start_bit == 24

        frame_ccv1 = result.frames[0x98FEF1FE]  # type: can_decoder.Frame
        assert frame_ccv1.id == 0x98FEF1FE
        assert frame_ccv1.multiplexer is None
        assert frame_ccv1.size == 8
        assert len(frame_ccv1.signals) == 1

        signal_vehicle_speed = frame_ccv1.signals[0]
        assert signal_vehicle_speed.is_float is False
        assert signal_vehicle_speed.is_little_endian is True
        assert signal_vehicle_speed.is_multiplexer is False
        assert signal_vehicle_speed.is_signed is False
        assert signal_vehicle_speed.name == "WheelBasedVehicleSpeed"
        assert signal_vehicle_speed.factor == 0.00390625
        assert signal_vehicle_speed.offset == 0
        assert signal_vehicle_speed.size == 16
        assert signal_vehicle_speed.start_bit == 8

        return

    @pytest.mark.parametrize(
        ("input_type",),
        [(LoadDBCPathType.LoadDBCPathType_STR,), (LoadDBCPathType.LoadDBCPathType_PATH,),
         (LoadDBCPathType.LoadDBCPathType_FILE,), (LoadDBCPathType.LoadDBCPathType_MEMORY,)]
    )
    def test_load_obd2_dbc(self, input_type: LoadDBCPathType):
        dbc_base_path = Path(__file__).parent.parent / "examples" / "CSS-Electronics-OBD2-v1.3.dbc"

        if input_type == LoadDBCPathType.LoadDBCPathType_STR:
            result = can_decoder.load_dbc(str(dbc_base_path))
        elif input_type == LoadDBCPathType.LoadDBCPathType_PATH:
            result = can_decoder.load_dbc(dbc_base_path)
        elif input_type == LoadDBCPathType.LoadDBCPathType_FILE:
            with open(dbc_base_path, "rb") as handle:
                result = can_decoder.load_dbc(handle)
        elif input_type == LoadDBCPathType.LoadDBCPathType_MEMORY:
            with open(dbc_base_path, "rb") as handle:
                raw = handle.read()

            with BytesIO(raw) as handle:
                result = can_decoder.load_dbc(handle)

        # Ensure that a DB is loaded.
        assert result is not None, "Expected a DB to be loaded"

        # Ensure the protocol is set to J1939.
        assert result.protocol == "OBD2", "Expected protocol to be OBD2"

        # Ensure the correct signals are present.
        assert len(result.frames) == 1
        assert 0x7E8 in result.frames.keys()

        frame = result.frames[0x7E8]  # type: can_decoder.Frame
        assert frame.id == 0x7E8
        assert frame.multiplexer is None
        assert frame.size == 8
        assert len(frame.signals) == 3

        signal_service = frame.signals[0]
        assert signal_service.name == "service"
        assert signal_service.is_multiplexer is True
        assert signal_service.size == 4
        assert signal_service.start_bit == 12
        assert len(signal_service.signals) == 2

        signal_service_1 = signal_service.signals[1]
        assert signal_service_1.name == "ParameterID_Service01"
        assert signal_service_1.is_multiplexer is True
        assert signal_service_1.size == 8
        assert signal_service_1.start_bit == 16
        assert len(signal_service_1.signals) == 114

        signal_service_freeze_dtc = signal_service_1.signals[2]
        assert signal_service_freeze_dtc.name == "S1_PID_02_FreezeDTC"
        assert signal_service_freeze_dtc.factor == 1
        assert signal_service_freeze_dtc.is_float is False
        assert signal_service_freeze_dtc.is_little_endian is False
        assert signal_service_freeze_dtc.is_multiplexer is False
        assert signal_service_freeze_dtc.is_signed is False
        assert signal_service_freeze_dtc.offset == 0
        assert signal_service_freeze_dtc.size == 16
        assert signal_service_freeze_dtc.start_bit == 24
        assert len(signal_service_freeze_dtc.signals) == 0

        signal_response = frame.signals[1]
        assert signal_response.name == "response"
        assert signal_response.is_float is False
        assert signal_response.is_little_endian is False
        assert signal_response.is_multiplexer is False
        assert signal_response.is_signed is False
        assert signal_response.size == 4
        assert signal_response.start_bit == 8
        assert len(signal_response.signals) == 0

        signal_length = frame.signals[2]
        assert signal_length.name == "length"
        assert signal_length.is_float is False
        assert signal_length.is_little_endian is False
        assert signal_length.is_multiplexer is False
        assert signal_length.is_signed is False
        assert signal_length.size == 8
        assert signal_length.start_bit == 0
        assert len(signal_length.signals) == 0

        return

    def test_load_with_invalid_object(self):
        with pytest.raises(OSError):
            can_decoder.load_dbc(45)

    pass
