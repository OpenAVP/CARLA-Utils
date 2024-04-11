import carla
import time

from .SensorData import SensorData
from ..Transform import Transform
from ..Vector3 import Vector3


class ImuData(SensorData):

    def __init__(self):
        super().__init__()
        self.accelerometer = Vector3()
        self.gyroscope = Vector3()
        self.compass = 0.0

    @classmethod
    def from_carla_measurements(cls, measurements: carla.IMUMeasurement) -> 'ImuData':
        """
        Load data from a carla.SensorData instance.
        :param measurements: cara.SensorData instance
        :return: SensorData instance
        """
        data = cls()
        data.frame = measurements.frame
        data.timestamp_carla = measurements.timestamp
        data.timestamp_wall = time.time()
        data.transform = Transform.from_carla_transform(measurements.transform)

        # special imu data
        data.accelerometer = Vector3.from_carla_vector3d(measurements.accelerometer)
        data.gyroscope = Vector3.from_carla_vector3d(measurements.gyroscope)
        data.compass = measurements.compass

        return data
