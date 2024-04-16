import carla

from .Sensor import Sensor
from ..core.data import RadarData


class Radar(Sensor):
    """
    A camera sensor.
    """

    def __init__(self, blueprint_name: str, **kwargs):
        super().__init__(blueprint_name, **kwargs)
        if 'sensor.other.radar' not in blueprint_name:
            raise TypeError(f'Blueprint {blueprint_name} is not a radar blueprint')

    @property
    def data(self) -> RadarData:
        """
        A sensor data snapshot.
        :return:
        """
        return self._data

    def listener(self, measurement: carla.Image):
        """
        The main listener function for the sensor.

        This method will update data and raise event_data_update.

        :param measurement: Sensor data, given by the carla.Sensor.listen() function callback.
        :return:
        """
        # dump sensor data
        self._data = RadarData.from_carla_measurements(measurement)
        # flash the event
        self._event_data_update.set()
        self._event_data_update.clear()