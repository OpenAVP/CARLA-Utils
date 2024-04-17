import carla
from typing import List

from .SensorData import SensorData


class RadarData(SensorData):
    """
    A class to store Radar data.
    """

    class Point:
        """
        A point in the radar data.
        """
        def __init__(self, altitude: float, azimuth: float, depth: float, velocity: float):
            self.altitude = altitude
            self.azimuth = azimuth
            self.depth = depth
            self.velocity = velocity

    def __init__(self):
        super().__init__()
        self.points = []  # type: List[RadarData.Point]

    @classmethod
    def from_carla_measurements(cls, measurements: carla.RadarMeasurement) -> 'RadarData':
        """
        Load data from a carla.RadarMeasurement instance.
        :param measurements: cara.RadarMeasurement instance
        :return: SensorData instance
        """
        data = cls()  # type: RadarData
        data = cls.initialize_sensor_basic_data(data, measurements)

        # special gnss data
        for detection in measurements:
            data.points.append(RadarData.Point(
                detection.altitude,
                detection.azimuth,
                detection.depth,
                detection.velocity
            ))

        return data
