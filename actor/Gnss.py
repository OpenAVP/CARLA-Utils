import carla

from .Sensor import Sensor
from ..core.data import GnssData


class Gnss(Sensor):

    def __init__(self, blueprint_name: str, **kwargs):
        super().__init__(blueprint_name, **kwargs)
        if 'sensor.other.gnss' not in blueprint_name:
            raise TypeError(f'Blueprint {blueprint_name} is not a gnss blueprint')

    @property
    def data(self) -> GnssData:
        """
        A sensor data snapshot.
        """
        return self._data

    def listener(self, measurement: carla.GnssMeasurement):
        """
        The main listener function for the sensor.

        This method will update data and raise event_data_update.

        :param measurement: Sensor data, given by the carla.Sensor.listen() function callback.
        :return:
        """
        # dump sensor data
        self._data = GnssData.from_carla_measurements(measurement)
        # flash the event
        self._event_data_update.set()
        self._event_data_update.clear()