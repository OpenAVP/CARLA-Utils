import carla

from .Location import Location
from .Rotation import Rotation


class Transform:
    """
    A data model class to represent a transformation of a 3D object.
    Includes location and rotation.
    """

    def __init__(self, *,
                 x: float = 0.0,
                 y: float = 0.0,
                 z: float = 0.0,
                 pitch: float = 0.0,
                 yaw: float = 0.0,
                 roll: float = 0.0):
        self.location = Location(x=x, y=y, z=z)
        self.rotation = Rotation(pitch=pitch, yaw=yaw, roll=roll)

    def as_carla_transform(self) -> carla.Transform:
        """
        Convert this Transform object to a carla.Transform object.

        :return: carla.Transform
        """
        return carla.Transform(
            location=self.location.as_carla_location(),
            rotation=self.rotation.as_carla_rotation()
        )

    @staticmethod
    def from_carla_transform(carla_transform: carla.Transform) -> 'Transform':
        """
        Convert a carla.Transform object to a Transform object.

        :param carla_transform: carla.Transform object
        :return: Transform object
        """
        return Transform(
            x=carla_transform.location.x,
            y=carla_transform.location.y,
            z=carla_transform.location.z,
            pitch=carla_transform.rotation.pitch,
            yaw=carla_transform.rotation.yaw,
            roll=carla_transform.rotation.roll
        )

    @staticmethod
    def from_location_and_rotation(location: Location, rotation: Rotation) -> 'Transform':
        """
        Create a Transform object from a Location and a Rotation object.

        :param location: Location object
        :param rotation: Rotation object
        :return: Transform object
        """
        tf = Transform()
        tf.location = location
        tf.rotation = rotation
        return tf
