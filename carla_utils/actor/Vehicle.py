import carla
from typing import Union

from .Actor import Actor
from ..core.data import VehicleStatusData
from ..core.setting import VehicleAckermannControlSettings
from ..core.cmd import VehicleAckermannControlCmd, VehicleDirectControlCmd


class Vehicle(Actor):
    """
    Vehicle is a wrapper for carla.Vehicle.
    """

    def __init__(self, blueprint_name: str):
        super().__init__(blueprint_name)

    @property
    def carla_actor(self) -> carla.Vehicle:
        """
        [Immutable] A carla.Vehicle instance.
        Get the carla vehicle instance if it is spawned, otherwise return None.
        """
        return super().carla_actor

    @property
    def status(self) -> VehicleStatusData:
        """
        Dump the vehicle status data.
        :return: VehicleStatusData instance.
        """
        return VehicleStatusData.from_carla_vehicle(self.carla_actor)

    @property
    def ackermann_control_settings(self) -> VehicleAckermannControlSettings:
        """
        Get the ackermann control settings.
        :return: VehicleAckermannControlSettings instance.
        """
        settings = self.carla_actor.get_ackermann_controller_settings()
        return VehicleAckermannControlSettings.from_carla_ackermann_controller_settings(settings)

    def set_ackermann_control_settings(self, setting: VehicleAckermannControlSettings) -> 'Vehicle':
        """
        Set the ackermann control settings.
        :param setting: VehicleAckermannControlSettings instance.
        :return: return self for method chaining.
        """
        self.is_alive(raise_exception=True)
        self.carla_actor.apply_ackermann_controller_settings(setting.as_carla_ackermann_controller_settings())
        return self

    def invoke_ackermann_control(self, cmd: VehicleAckermannControlCmd) -> 'Vehicle':
        """
        Invoke the ackermann control command.
        :param cmd: VehicleAckermannControlCmd instance.
        :return: return self for method chaining.
        :raises RuntimeError: if the vehicle is not alive.
        """
        self.is_alive(raise_exception=True)
        self.carla_actor.apply_ackermann_control(cmd.as_carla_vehicle_ackermann_control())
        return self

    def invoke_direct_control(self, cmd: VehicleDirectControlCmd) -> 'Vehicle':
        """
        Invoke the direct control command.
        :param cmd: VehicleDirectControlCmd instance.
        :return: return self for method chaining.
        :raises RuntimeError: if the vehicle is not alive.
        """
        self.is_alive(raise_exception=True)
        self.carla_actor.apply_control(cmd.as_carla_vehicle_control())
        return self

    def override_ackermann_control_settings(self, *,
                                              speed_kp: Union[float, None] = None,
                                              speed_ki: Union[float, None] = None,
                                              speed_kd: Union[float, None] = None,
                                              accel_kp: Union[float, None] = None,
                                              accel_ki: Union[float, None] = None,
                                              accel_kd: Union[float, None] = None) -> 'Vehicle':
        """
        Override the ackermann control settings.

        :param speed_kp: speed PID controller proportional gain.
        :param speed_ki: speed PID controller integral gain.
        :param speed_kd: speed PID controller derivative gain.
        :param accel_kp: acceleration PID controller proportional gain.
        :param accel_ki: acceleration PID controller integral gain.
        :param accel_kd: acceleration PID controller derivative gain.
        :return: return self for method chaining.
        """
        self.is_alive(raise_exception=True)
        # get current settings
        settings = self.ackermann_control_settings
        # override items
        if speed_kp is not None:
            settings.speed_kp = speed_kp
        if speed_ki is not None:
            settings.speed_ki = speed_ki
        if speed_kd is not None:
            settings.speed_kd = speed_kd
        if accel_kp is not None:
            settings.accel_kp = accel_kp
        if accel_ki is not None:
            settings.accel_ki = accel_ki
        if accel_kd is not None:
            settings.accel_kd = accel_kd
        # set new settings
        self.set_ackermann_control_settings(settings)
        # and return
        return self

    def override_direct_control(self, *,
                                throttle: Union[float, None] = None,
                                steer: Union[float, None] = None,
                                brake: Union[float, None] = None,
                                hand_brake: Union[bool, None] = None,
                                reverse: Union[bool, None] = None,
                                manual_gear_shift: Union[bool, None],
                                manual_gear: Union[bool, None]) -> 'Vehicle':
        """
        Override the direct control command.

        :param throttle: accelerator pedal opening in [0.0, 1.0].
                         Exceeding values will be reset to the maximum or minimum value
        :param steer: steering wheel angle in [-1.0, 1.0].
                      Exceeding values will be reset to the maximum or minimum value
        :param brake: brake pedal opening in [0.0, 1.0].
                      Exceeding values will be reset to the maximum or minimum value
        :param hand_brake: hand brake status
        :param reverse: reverse manual_gear status
        :param manual_gear_shift: manual manual_gear shift status
        :param manual_gear: manual_gear to shift to, effective only when manual_gear_shift is True
        :return: return self for method chaining.
        """
        self.is_alive(raise_exception=True)
        # get current status
        status = self.status
        # generate new control command
        cmd = VehicleDirectControlCmd()
        cmd.throttle = throttle if throttle is not None else status.throttle
        cmd.steer = steer if steer is not None else status.steer
        cmd.brake = brake if brake is not None else status.brake
        cmd.hand_brake = hand_brake if hand_brake is not None else status.hand_brake
        cmd.reverse = reverse if reverse is not None else status.reverse
        cmd.manual_gear_shift = manual_gear_shift if manual_gear_shift is not None else status.manual_gear_shift
        cmd.manual_gear = manual_gear if manual_gear is not None else status.gear
        # invoke the control
        self.invoke_direct_control(cmd)
        # and return
        return self

    def override_visual_steer_angle(self, *,
                                    steer_fl: Union[float, None] = None,
                                    steer_fr: Union[float, None] = None,
                                    steer_rl: Union[float, None] = None,
                                    steer_rr: Union[float, None] = None) -> 'Vehicle':
        """
        Override the visual steer angle of each wheel.

        No effect on the vehicle physics.

        :param steer_fl: steer angle of the front left wheel, in degree.
        :param steer_fr: steer angle of the front right wheel, in degree.
        :param steer_rl: steer angle of the rear left wheel, in degree.
        :param steer_rr: steer angle of the rear right wheel, in degree.
        :return: return self for method chaining.
        :raises RuntimeError: if the vehicle is not alive.
        """
        self.is_alive(raise_exception=True)
        # get current status
        target_fl = self.status.wheel_steer_angle_FL
        target_fr = self.status.wheel_steer_angle_FR
        target_RL = self.status.wheel_steer_angle_RL
        target_RR = self.status.wheel_steer_angle_RR
        # override items
        target_fl = steer_fl if steer_fl is not None else target_fl
        target_fr = steer_fr if steer_fr is not None else target_fr
        target_RL = steer_rl if steer_rl is not None else target_RL
        target_RR = steer_rr if steer_rr is not None else target_RR
        # set visual steer angle
        self.carla_actor.set_wheel_steer_direction(carla.VehicleWheelLocation.FL_Wheel, target_fl)
        self.carla_actor.set_wheel_steer_direction(carla.VehicleWheelLocation.FR_Wheel, target_fr)
        self.carla_actor.set_wheel_steer_direction(carla.VehicleWheelLocation.BL_Wheel, target_RL)
        self.carla_actor.set_wheel_steer_direction(carla.VehicleWheelLocation.BR_Wheel, target_RR)
        # and return
        return self
