import carla
import math


class Vector3:
    """
    A data model class to represent a 3D vector.

    Similar 3D vectors in different software defined coordinate systems should be converted to Vector3 and promoted
    in the context.

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
        Construct a default Vector3 instance.

        :param x: the x-coordinate of the vector
        :param y: the y-coordinate of the vector
        :param z: the z-coordinate of the vector
        """
        self.x = x
        self.y = y
        self.z = z

    @property
    def magnitude(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def as_carla_vector3d(self) -> carla.Vector3D:
        """
        Convert the Vector3 instance to a carla.Vector3D instance.

        :return: carla.Vector3D instance
        """
        return carla.Vector3D(x=self.x, y=self.y, z=self.z)

    @classmethod
    def from_carla_vector3d(cls, carla_vector3d: carla.Vector3D) -> 'Vector3':
        """
        Convert a carla.Vector3D instance to a Vector3 instance.

        :param carla_vector3d: carla.Vector3D instance
        :return: Vector3
        """
        return cls(x=carla_vector3d.x, y=carla_vector3d.y, z=carla_vector3d.z)
