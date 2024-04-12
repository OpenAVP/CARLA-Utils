import carla
import numpy
from typing import List, Optional

from .SensorData import SensorData


class LidarData(SensorData):
    """
    A class to store Lidar data.
    """

    class Point:
        """
        A point in the lidar data.
        """
        def __init__(self, x: float, y: float, z: float, intensity: float):
            self.x = x
            self.y = y
            self.z = z
            self.intensity = intensity

    def __init__(self):
        super().__init__()
        self.points = []  # type: List[LidarData.Point]
        self.points_ndarray = None  # Optional[numpy.ndarray]
        self.channels = 0
        self.horizontal_angle = 0

    @classmethod
    def from_carla_measurements(cls, measurements: carla.LidarMeasurement) -> 'LidarData':
        """
        Load data from a carla.RadarMeasurement instance.
        :param measurements: cara.RadarMeasurement instance
        :return: SensorData instance
        """
        data = cls()  # type: LidarData
        data = cls.initialize_sensor_basic_data(data, measurements)

        # special gnss data
        data.channels = carla.LidarMeasurement.channels
        data.horizontal_angle = carla.LidarMeasurement.horizontal_angle
        data.points_ndarray = numpy.frombuffer(data.raw_data, dtype=numpy.dtype([
            ('x', numpy.float32),
            ('y', numpy.float32),
            ('z', numpy.float32),
            ('intensity', numpy.float32)]))
        for i in range(0, len(data.points_ndarray)):
            data.points.append(LidarData.Point(data.points_ndarray[i][0],
                                               data.points_ndarray[i][1],
                                               data.points_ndarray[i][2],
                                               data.points_ndarray[i][3]))

        return data
