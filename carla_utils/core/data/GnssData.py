import carla

from .SensorData import SensorData


class GnssData(SensorData):
    """
    A class to store GNSS data.
    """

    def __init__(self):
        super().__init__()
        self.altitude = 0.0
        self.latitude = 0.0
        self.longitude = 0.0

    @classmethod
    def from_carla_measurements(cls, measurements: carla.GnssMeasurement) -> 'GnssData':
        """
        Load data from a carla.SensorData instance.
        :param measurements: cara.SensorData instance
        :return: SensorData instance
        """
        data = cls()  # type: GnssData
        data = cls.initialize_sensor_basic_data(data, measurements)

        # special gnss data
        data.altitude = float(measurements.altitude)
        data.latitude = float(measurements.latitude)
        data.longitude = float(measurements.longitude)

        return data
