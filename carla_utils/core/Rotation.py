import carla

from .Vector3 import Vector3


class Rotation(Vector3):
    """
    A class to represents a rotation in 3D space.

    The right side is the positive direction and is described in terms of angles in degrees.

    Coordinate system is defined as same as UE4 and CARLA:

        - X-axis: rotation angle in degrees
        - Y-axis: pitch angle in degrees
        - Z-axis: yaw angle in degrees

    """

    def __init__(self, *,
                 roll: float = 0.0,
                 pitch: float = 0.0,
                 yaw: float = 0.0):
        super().__init__(x=roll, y=pitch, z=yaw)
        self.roll = self.x
        self.pitch = self.y
        self.yaw = self.z

    def as_carla_rotation(self) -> carla.Rotation:
        """
        Convert the Rotation to a carla.Rotation object.

        :return: carla.Rotation object
        """
        return carla.Rotation(roll=self.roll, pitch=self.pitch, yaw=self.yaw)

    @staticmethod
    def from_carla_rotation(carla_rotation: carla.Rotation) -> 'Rotation':
        """
        Convert a carla.Rotation object to a Rotation object.

        :param carla_rotation: carla.Rotation object
        :return: Rotation object
        """
        return Rotation(roll=carla_rotation.roll, pitch=carla_rotation.pitch, yaw=carla_rotation.yaw)