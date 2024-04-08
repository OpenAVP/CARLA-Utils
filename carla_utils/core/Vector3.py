class Vector3:
    """
    A class to represent a 3D vector.
    """

    def __init__(self,
                 x: float,
                 y: float,
                 z: float):
        """
        Construct a default Vector3 object.

        :param x: the x-coordinate of the vector
        :param y: the y-coordinate of the vector
        :param z: the z-coordinate of the vector
        """
        self.x = x
        self.y = y
        self.z = z
