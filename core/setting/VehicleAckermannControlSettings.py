import carla


class VehicleAckermannControlSettings:
    """
    A class to hold the settings for the Ackermann control of a vehicle.
    """

    class PIDSettings:
        """
        A class to hold the settings for a PID controller.
        """

        def __init__(self, kp=0.0, ki=0.0, kd=0.0):
            self.kp = kp
            self.ki = ki
            self.kd = kd

    def __init__(self):
        self.speed = self.PIDSettings()
        self.accel = self.PIDSettings()

    def as_carla_ackermann_controller_settings(self) -> carla.AckermannControllerSettings:
        """
        Convert VehicleAckermannControlSettings to carla.VehicleControl.
        """
        settings = carla.AckermannControllerSettings()
        settings.speed_kp = self.speed.kp
        settings.speed_ki = self.speed.ki
        settings.speed_kd = self.speed.kd
        settings.acceleration_kp = self.accel.kp
        settings.acceleration_ki = self.accel.ki
        settings.acceleration_kd = self.accel.kd
        return settings

    @classmethod
    def from_carla_ackermann_controller_settings(cls, settings: carla.AckermannControllerSettings) \
            -> 'VehicleAckermannControlSettings':
        """
        Convert a carla.VehicleControl to VehicleAckermannControlSettings.
        """
        obj = cls()
        obj.speed.kp = settings.speed_kp
        obj.speed.ki = settings.speed_ki
        obj.speed.kd = settings.speed_kd
        obj.accel.kp = settings.acceleration_kp
        obj.accel.ki = settings.acceleration_ki
        obj.accel.kd = settings.acceleration_kd
        return obj
