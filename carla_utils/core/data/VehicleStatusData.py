import carla
from typing import Union

from ..Vector3 import Vector3


class VehicleStatusData:
    """
    A data class representing the status of a vehicle.
    Including basic info and pyhsics info.
    """

    def __init__(self):
        """
        Construct a new VehicleStatusData instance.
        """
        # basic info
        self.speed = None  # type: Union[float, None]  # m/s
        self.velocity = None  # type: Union[Vector3, None]  # m/s in x, y, z
        self.acceleration = None  # type: Union[Vector3, None]  # m/s^2 in x, y, z
        # basic control info
        self.throttle = None  # type: Union[float, None]
        self.steer = None  # type: Union[float, None]
        self.brake = None  # type: Union[float, None]
        self.hand_brake = None  # type: Union[bool, None]
        self.reverse = None  # type: Union[bool, None]
        self.manual_gear_shift = None  # type: Union[bool, None]
        self.gear = None  # type: Union[int, None]
        # wheel steer angles
        self.wheel_steer_angle_FL = None  # type: Union[float, None]
        self.wheel_steer_angle_FR = None  # type: Union[float, None]
        self.wheel_steer_angle_RL = None  # type: Union[float, None]
        self.wheel_steer_angle_RR = None  # type: Union[float, None]

    def __new__(cls, *args, **kwargs):
        # Prevent instantiation of this class
        raise NotImplementedError(f'Cannot instantiate {cls.__name__}. '
                                  f'Use from_carla_vehicle_control instead.')

    @classmethod
    def from_carla_vehicle(cls, vehicle: carla.Vehicle) -> 'VehicleStatusData':
        """
        Create a VehicleStatusData instance from a carla.VehicleControl instance.
        """
        data = cls.__new__(cls)
        # basic info
        data.velocity = Vector3.from_carla_vector3d(vehicle.get_velocity())
        data.acceleration = Vector3.from_carla_vector3d(vehicle.get_acceleration())
        data.speed = data.velocity.magnitude
        # basic control info
        if not isinstance(vehicle, carla.Vehicle):
            return data
        control = vehicle.get_control()
        data.throttle = control.throttle
        data.steer = control.steer
        data.brake = control.brake
        data.hand_brake = control.hand_brake
        data.reverse = control.reverse
        data.manual_gear_shift = control.manual_gear_shift
        data.gear = control.manual_gear
        # steer angles
        data.wheel_steer_angle_FL = vehicle.get_wheel_steer_angle(carla.VehicleWheelLocation.FL_Wheel)
        data.wheel_steer_angle_FR = vehicle.get_wheel_steer_angle(carla.VehicleWheelLocation.FR_Wheel)
        data.wheel_steer_angle_RL = vehicle.get_wheel_steer_angle(carla.VehicleWheelLocation.BL_Wheel)
        data.wheel_steer_angle_RR = vehicle.get_wheel_steer_angle(carla.VehicleWheelLocation.BR_Wheel)
        return data
