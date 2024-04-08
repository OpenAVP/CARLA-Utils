import carla

from .Vector3 import Vector3


class Location(Vector3):
    """
    A class to represent a location in the world.

    Coordinate system is defined as same as UE4 and CARLA:

        - X-axis: forward
        - Y-axis: right
        - Z-axis: up
    """

    def __init__(self, *,
                 x: float = 0.0,
                 y: float = 0.0,
                 z: float = 0.0):
        """
        Construct a default Location object.

        :param x: distance from the origin along the X-axis
        :param y: distance from the origin along the Y-axis
        :param z: distance from the origin along the Z-axis
        """
        super().__init__()

    def as_carla_location(self) -> carla.Location:
        """
        Convert this location to a CARLA location.

        :return: carla.Location object
        """
        return carla.Location(x=self.x, y=self.y, z=self.z)

    @staticmethod
    def from_carla_location(carla_location: carla.Location) -> 'Location':
        """
        Convert a carla.Location to a Location object.

        :param carla_location: carla.Location object
        :return: Location object
        """
        return Location(x=carla_location.x, y=carla_location.y, z=carla_location.z)