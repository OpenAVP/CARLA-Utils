import carla

from typing import Union


class VehicleStatusData:
    """
    A data class representing the status of a vehicle.
    Including basic info and pyhsics info.
    """

    def __init__(self):
        """
        Construct a new VehicleStatusData instance.
        """
        self.throttle = None  # type: Union[float, None]
        self.steer = None  # type: Union[float, None]
        self.brake = None  # type: Union[float, None]
        self.hand_brake = None  # type: Union[bool, None]
        self.reverse = None  # type: Union[bool, None]
        self.manual_gear_shift = None  # type: Union[bool, None]
        self.gear = None  # type: Union[int, None]

    def __new__(cls, *args, **kwargs):
        # Prevent instantiation of this class
        raise NotImplementedError(f'Cannot instantiate {cls.__name__}. '
                                  f'Use from_carla_vehicle_control instead.')

    @classmethod
    def from_carla_vehicle_control(cls, control: carla.VehicleControl) -> 'VehicleStatusData':
        """
        Create a VehicleStatusData instance from a carla.VehicleControl instance.
        """
        data = cls.__new__(cls)
        data.throttle = control.throttle
        data.steer = control.steer
        data.brake = control.brake
        data.hand_brake = control.hand_brake
        data.reverse = control.reverse
        data.manual_gear_shift = control.manual_gear_shift
        data.gear = control.gear
        return data
