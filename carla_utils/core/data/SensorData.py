import time
import carla
from typing import Union

from ..Vector3 import Vector3

class SensorData:

    def __init__(self):
        self.frame = 0
        self.timestamp_carla = 0.0
        self.timestamp_wall = 0.0
        self.transform = None  # type: Union[None, Transform]
        self.raw_data = None

    def __new__(cls, *args, **kwargs):
        # Prevent instantiation of this class
        raise NotImplementedError(f'Cannot instantiate {cls.__name__}. Use from_carla_measurements instead.')

    @classmethod
    def from_carla_measurements(cls, measurements: carla.SensorData) -> 'SensorData':
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
        if hasattr(data, 'raw_data'):
            data.raw_data = measurements.raw_data
        return data
