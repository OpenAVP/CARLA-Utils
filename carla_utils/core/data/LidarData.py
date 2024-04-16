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
        data.channels = measurements.channels
        data.horizontal_angle = measurements.horizontal_angle
        data.points_ndarray = numpy.fromstring(data.raw_data, dtype=numpy.float32)
        data.points_ndarray = numpy.reshape(data.points_ndarray, (int(data.points_ndarray.shape[0] / 4), 4))
        for i in range(0, len(data.points_ndarray)):
            data.points.append(LidarData.Point(data.points_ndarray[i][0],
                                               data.points_ndarray[i][1],
                                               data.points_ndarray[i][2],
                                               data.points_ndarray[i][3]))

        # TODO: There is a bug causing the 0 points received from the lidar sensor
        # print(len(data.points))

        return data
