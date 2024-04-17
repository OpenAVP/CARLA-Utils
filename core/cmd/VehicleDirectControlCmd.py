import carla


class VehicleDirectControlCmd:
    """
    A command class representing the direct control command for a vehicle.
    """

    def __init__(self, *,
                 throttle: float = 0.0,
                 steer: float = 0.0,
                 brake: float = 0.0,
                 hand_brake: bool = False,
                 reverse: bool = False,
                 manual_gear_shift: bool = False,
                 manual_gear: int = 0):
        """
        Construct a VehicleDirectControlCmd instance.

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
        """
        self.throttle = throttle
        self.steer = steer
        self.brake = brake
        self.hand_brake = hand_brake
        self.reverse = reverse
        self.manual_gear_shift = manual_gear_shift
        self.manual_gear = manual_gear

    def as_carla_vehicle_control(self) -> carla.VehicleControl:
        """
        Convert the command to a carla.VehicleControl object.
        :return: carla.VehicleControl instance
        """
        # clean data
        throttle = max(0.0, min(1.0, self.throttle))
        steer = max(-1.0, min(1.0, self.steer))
        brake = max(0.0, min(1.0, self.brake))
        # construct and return
        return carla.VehicleControl(
            throttle=throttle,
            steer=steer,
            brake=brake,
            hand_brake=self.hand_brake,
            reverse=self.reverse,
            manual_gear_shift=self.manual_gear_shift,
            gear=self.manual_gear
        )
