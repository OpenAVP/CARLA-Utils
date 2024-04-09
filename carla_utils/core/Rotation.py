import carla

from .Vector3 import Vector3


class Rotation(Vector3):
    """
    A data model class to represents a rotation in 3D space.

    Coordinate system is defined as same as UE4 and CARLA:

        - Right side positive
        - Angles are in degrees
        - X-axis: roll
        - Y-axis: pitch
        - Z-axis: yaw

    """

    def __init__(self, *,
                 roll: float = 0.0,
                 pitch: float = 0.0,
                 yaw: float = 0.0):
        """
        Construct a default Rotation instance.

        :param roll: the x-axis rotation angle in degrees
        :param pitch: the y-axis rotation angle in degrees
        :param yaw: the z-axis rotation angle in degrees
        """
        super().__init__(x=roll, y=pitch, z=yaw)

    @property
    def roll(self) -> float:
        return self.x

    @roll.setter
    def roll(self, value: float):
        self.x = value

    @property
    def pitch(self) -> float:
        return self.y

    @pitch.setter
    def pitch(self, value: float):
        self.y = value

    @property
    def yaw(self) -> float:
        return self.z

    @yaw.setter
    def yaw(self, value: float):
        self.z = value

    def as_carla_rotation(self) -> carla.Rotation:
        """
        Convert the Rotation to a carla.Rotation instance.

        :return: carla.Rotation instance
        """
        return carla.Rotation(roll=self.roll, pitch=self.pitch, yaw=self.yaw)

    @classmethod
    def from_carla_rotation(cls, carla_rotation: carla.Rotation) -> 'Rotation':
        """
        Convert a carla.Rotation instance to a Rotation instance.

        :param carla_rotation: carla.Rotation instance
        :return: Rotation instance
        """
        return cls(roll=carla_rotation.roll, pitch=carla_rotation.pitch, yaw=carla_rotation.yaw)