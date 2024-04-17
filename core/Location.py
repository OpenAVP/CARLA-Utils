import carla

from .Vector3 import Vector3


class Location(Vector3):
    """
    A data model class to represent a location in the world.

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
        Construct a default Location instance.

        :param x: distance from the origin along the X-axis
        :param y: distance from the origin along the Y-axis
        :param z: distance from the origin along the Z-axis
        """
        super().__init__(x=x, y=y, z=z)

    def as_carla_location(self) -> carla.Location:
        """
        Convert this location to a CARLA location.

        :return: carla.Location instance
        """
        return carla.Location(x=self.x, y=self.y, z=self.z)

    @classmethod
    def from_carla_location(cls, carla_location: carla.Location) -> 'Location':
        """
        Convert a carla.Location to a Location instance.

        :param carla_location: carla.Location instance
        :return: Location instance
        """
        return cls(x=carla_location.x, y=carla_location.y, z=carla_location.z)