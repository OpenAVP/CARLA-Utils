import carla


class VehicleAckermannControlCmd:
    """
    A command class representing the ackermann control for a vehicle.
    """

    def __init__(self, *,
                 steer: float = 0.0,
                 steer_speed: float = 0.0,
                 speed: float = 0.0,
                 acceleration: float = 0.0,
                 jerk: float = 0.0):
        """
        Construct a VehicleAckermannControlCmd instance.

        :param steer: Desired steer in rad. Positive value represent right steer
        :param steer_speed: Steering velocity in rad/s. 0.0 means steering as fast as possible
        :param speed: Desired speed in m/s.
        :param acceleration: Desired acceleration in m/s2.
        :param jerk: Desired jerk in m/s3.
        """
        self.steer = steer
        self.steer_speed = steer_speed
        self.speed = speed
        self.acceleration = acceleration
        self.jerk = jerk

    def as_carla_vehicle_ackermann_control(self) -> carla.VehicleAckermannControl:
        """
        Convert to carla.VehicleAckermannControl object.
        :return: carla.VehicleAckermannControl instance.
        """
        return carla.VehicleAckermannControl(
            steer=self.steer,
            steer_speed=self.steer_speed,
            speed=self.speed,
            acceleration=self.acceleration,
            jerk=self.jerk
        )
