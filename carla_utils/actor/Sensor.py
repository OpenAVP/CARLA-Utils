import carla
from threading import Event

from .Actor import Actor
from ..core.data import SensorData


class Sensor(Actor):
    """
    Sensor is a wrapper class for carla.Sensor.
    """

    def __init__(self, blueprint_name: str):
        """
        Construct a Sensor instance.
        :param blueprint_name:
        """
        super().__init__(blueprint_name)
        self._data = None
        self._event_data_update = Event()
        self._sensor_data_class = SensorData
        if not issubclass(self._sensor_data_class, SensorData):
            raise ValueError("sensor_data_class must be a subclass of SensorData.")

    @property
    def carla_actor(self) -> carla.Sensor:
        """
        [Immutable] A carla.Sensor instance.
        Get the carla sensor instance if it is spawned, otherwise return None.
        """
        return super().carla_actor

    @property
    def data(self) -> SensorData:
        """
        A sensor data snapshot.
        :return:
        """
        return self._data

    @property
    def event_data_update(self) -> Event:
        """
        A data update event.
        :return: threading.Event
        """
        return self._event_data_update

    def invoke_start_listen(self) -> 'Sensor':
        pass

    def invoke_stop_listen(self) -> 'Sensor':
        pass

    def listener(self, measurement: carla.SensorData):
        """
        The main listener function for the sensor.

        This method will update data and raise event_data_update.

        :param measurement: Sensor data, given by the carla.Sensor.listen() function callback.
        :return:
        """
        # dump sensor data
        self._data = self._sensor_data_class.from_carla_measurements(measurement)
        # flash the event
        self._event_data_update.set()
        self._event_data_update.clear()
