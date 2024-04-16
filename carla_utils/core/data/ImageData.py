import carla
import time
import numpy

from .SensorData import SensorData
from ..Transform import Transform


class ImageData(SensorData):

    def __init__(self):
        super().__init__()
        self.fov = 0.0
        self.height = 0
        self.width = 0
        self.image = None

    @classmethod
    def from_carla_measurements(cls,
                                measurements: carla.Image,
                                convert: carla.ColorConverter = carla.ColorConverter.Raw) -> 'ImageData':
        """
        Load data from a carla.SensorData instance.
        :param convert: carla.ColorConverter, convert a image to a different visualization form
        :param measurements: cara.SensorData instance
        :return: SensorData instance
        """
        data = cls()
        # dump data
        data = cls.initialize_sensor_basic_data(data, measurements)
        data.fov = measurements.fov
        data.height = measurements.height
        data.width = measurements.width

        # create image
        data.image = numpy.ndarray(
            shape=(data.height, data.width, 4),
            dtype=numpy.uint8,
            buffer=data.raw_data)

        return data

    def as_pygame_surface_data(self) -> numpy.ndarray:
        """
        Convert the image to a pygame surface.
        :return: pygame.Surface
        """
        img = self.image
        img = img[:, :, :3]
        img = img[:, :, ::-1]
        img = numpy.rot90(img)
        img = numpy.flip(img, 0)
        return img