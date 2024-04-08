import carla
import random


class Blueprint:
    """
    A data model class to represent a blueprint structure.

    This class temporary holds the blueprint with attribute needed to spawn the Actor.
    When actor spawn procedure invoked, this class will be converted to carla.Blueprint object.
    """

    def __init__(self, blueprint_name: str):
        """

        :param blueprint_name:
        """
        self._blueprint_name = blueprint_name  # read-only, expose by property method
        self.attributes = dict()

    @property
    def blueprint_name(self) -> str:
        return self._blueprint_name

    def set_attribute(self, key: str, value):
        """
        A method to set attribute value.

        :param key: attribute name
        :param value: attribute value, None is for random recommended value
        :raise TypeError: if key is not a string
        """
        if not isinstance(key, str):
            raise TypeError(f'key must be a string')
        if value:
            self.attributes[key] = str(value)
        else:
            self.attributes[key] = None

    def as_carla_blueprint(self, carla_world: carla.World) -> carla.ActorBlueprint:
        """
        A method to convert Blueprint to carla.ActorBlueprint object.

        Use carla.World to find the matched blueprint from the blueprint library.
        This method should be the last one called before the actor spawn.

        :param carla_world: carla.World object
        :return: carla.ActorBlueprint object
        :raise IndexError: if the blueprint not found in the world's blueprint library
                           or attribute not found in the blueprint

        """
        # type check
        if not isinstance(carla_world, carla.World):
            raise TypeError(f'carla_world must be a instance of carla.World')

        # find matched blueprint
        bp_lib = carla_world.get_blueprint_library()  # type: carla.BlueprintLibrary
        bp = bp_lib.find(self.blueprint_name)  # type: carla.ActorBlueprint

        # set attributes
        for key, value in self.attributes.items():
            attr = bp.get_attribute(key)
            if not attr:
                raise RuntimeError(f'Attribute {key} not found in blueprint {self.blueprint_name}')
            if not attr.is_modifiable:
                raise RuntimeError(f'Attribute {key} is not modifiable in blueprint {self.blueprint_name}')
            # use default value if value is None
            if value is None:
                value = random.choice(attr.recommended_values)
            # invoke set
            bp.set_attribute(key, value)

        # return the blueprint
        return bp