import carla

from .Sensor import Sensor
from ..core.data import ImuData


class Imu(Sensor):

    def __init__(self, blueprint_name: str, **kwargs):
        super().__init__(blueprint_name, **kwargs)
        if 'sensor.other.imu' not in blueprint_name:
            raise TypeError(f'Blueprint {blueprint_name} is not a imu blueprint')

    @property
    def data(self) -> ImuData:
        """
        A sensor data snapshot.
        """
        return self._data

    def listener(self, measurement: carla.IMUMeasurement):
        """
        The main listener function for the sensor.

        This method will update data and raise event_data_update.

        :param measurement: Sensor data, given by the carla.Sensor.listen() function callback.
        :return:
        """
        # dump sensor data
        self._data = ImuData.from_carla_measurements(measurement)
        # flash the event
        self._event_data_update.set()
        self._event_data_update.clear()