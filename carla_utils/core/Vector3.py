import carla


class Vector3:
    """
    A class to represent a 3D vector.

    Similar 3D vectors in different software defined coordinate systems should be converted to Vector3 and promoted
    in the context.

    Coordinate system is defined as same as UE4 and CARLA:

        - X-axis: forward
        - Y-axis: right
        - Z-axis: up

    """

    def __init__(self,
                 x: float = 0.0,
                 y: float = 0.0,
                 z: float = 0.0):
        """
        Construct a default Vector3 object.

        :param x: the x-coordinate of the vector
        :param y: the y-coordinate of the vector
        :param z: the z-coordinate of the vector
        """
        self.x = x
        self.y = y
        self.z = z

    def as_carla_vector3d(self) -> carla.Vector3D:
        """
        Convert the Vector3 object to a carla.Vector3D object.

        :return: carla.Vector3D
        """
        return carla.Vector3D(x=self.x, y=self.y, z=self.z)

    @staticmethod
    def from_carla_vector3d(self) -> 'Vector3':
        """
        Convert a carla.Vector3D object to a Vector3 object.

        :return: Vector3
        """
        return Vector3(x=self.x, y=self.y, z=self.z)
