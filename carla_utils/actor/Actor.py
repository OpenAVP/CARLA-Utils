import uuid
import carla
from typing import List, Union

from .Blueprint import Blueprint
from ..core import Transform, Vector3


class Actor:

    def __init__(self, blueprint_name: str):
        # basic info
        self._id = uuid.uuid1()
        self._blueprint = Blueprint(blueprint_name)
        self._transform_init = Transform()
        # actor tree
        self._parent = None
        self._children = []
        # carla actor instance
        self._carla_actor = None
        # options
        self._option_carla_physics = True

    def __del__(self):
        self.invoke_destroy(no_hook=True)

    @property
    def id(self) -> str:
        """
        Actor uuid, read-only
        """
        return str(self._id)

    @property
    def name(self) -> str:
        """
        Actor name, defined by the blueprint role_name attribute.
        """
        return self.blueprint.attributes.get('role_name', '')

    @name.setter
    def name(self, value: str):
        """
        Set the actor name.

        This method will update the role_name attribute of the blueprint.
        So, it's not allowed to set the name after the actor is spawned.

        :param value: new name
        :raise RuntimeError: if the actor is alive.
        """
        if self.is_alive():
            raise RuntimeError('name is not allowed to set after the actor is spawned.')
        self.blueprint.set_attribute('role_name', value)

    @property
    def carla_actor(self) -> carla.Actor:
        """
        [Immutable] A carla.Actor instance.
        Get the carla actor instance if it is spawned, otherwise return None.
        """
        return self._carla_actor

    @property
    def blueprint(self) -> Blueprint:
        """
        [Immutable] Actor blueprint.
        """
        return self._blueprint

    @property
    def transform(self) -> Transform:
        """
        [Immutable] Actor current transform.
        Get the transform of the carla actor if it is spawned, otherwise return the initial transform.
        """
        if not self.is_alive():
            return self.transform_init
        else:
            return Transform.from_carla_transform(self.carla_actor.get_transform())

    @property
    def transform_init(self) -> Transform:
        """
        [Immutable] Actor initial transform.
        """
        return self._transform_init

    @property
    def velocity(self) -> Vector3:
        """
        [Read-only] Velocity of the actor.
        :return: current velocity of the actor. Vector3(0, 0, 0) if the actor is not alive.
        """
        if self.is_alive():
            return Vector3.from_carla_vector3d(self.carla_actor.get_velocity())
        else:
            return Vector3()

    @property
    def angular_velocity(self) -> Vector3:
        """
        [Read-only] Angular velocity of the actor.
        :return: current angular velocity of the actor. Vector3(0, 0, 0) if the actor is not alive.
        """
        if self.is_alive():
            return Vector3.from_carla_vector3d(self.carla_actor.get_angular_velocity())
        else:
            return Vector3()

    @property
    def acceleration(self) -> Vector3:
        """
        [Read-only] Acceleration of the actor.
        :return: current acceleration of the actor. Vector3(0, 0, 0) if the actor is not alive.
        """
        if self.is_alive():
            return Vector3.from_carla_vector3d(self.carla_actor.get_acceleration())
        else:
            return Vector3()

    @property
    def parent(self) -> 'Actor':
        """
        [Immutable] Actor parent in actor tree.
        Note that the actor tree is maintained within the program, not CARLA server.
        """
        return self._parent

    @property
    def children(self) -> List['Actor']:
        """
        [Immutable] Actor children in actor tree.
        Note that the actor tree is maintained within the program, not CARLA server.
        """
        return self._children

    def is_alive(self, *, raise_exception=False) -> bool:
        """
        Check if the actor is spawned and alive.
        :param raise_exception: Optional, if True, raise exception when the actor is not alive.
        :return: True if the actor is alive, otherwise False.
        """
        if self.carla_actor and self.carla_actor.is_alive:
            return True
        elif raise_exception:
            raise RuntimeError(f"Actor {self.id} is not alive. Please check if it is spawned and alive.")
        else:
            return False

    def set_parent(self, parent: 'Actor') -> 'Actor':
        """
        Set the parent of the actor.

        Has the same effect as attach_to.

        :param parent: a Actor instance
        :return: return self for method chaining.
        """
        self._parent = parent
        parent.children.append(self)
        return self

    def set_attribute(self, key: str, value) -> 'Actor':
        """
        A proxy method to set attribute value for blueprint.

        :param key: attribute name
        :param value: attribute value, None is for random recommended value
        :raise TypeError: if key is not a string
        """
        self.blueprint.set_attribute(key, value)
        return self

    def set_transform(self, transform: Transform) -> 'Actor':
        """
        Set the transform of the actor.

        If the actor is spawned, move the actor to the new transform.
        Otherwise, update the initial transform.

        :param transform: Transform instance
        :return: return self for method chaining.
        """
        if self.is_alive():
            self.carla_actor.set_transform(transform.as_carla_transform())
        else:
            self._transform_init = transform

        return self

    def set_transform_direct(self, *,
                             x: Union[float, None] = None,
                             y: Union[float, None] = None,
                             z: Union[float, None] = None,
                             roll: Union[float, None] = None,
                             pitch: Union[float, None] = None,
                             yaw: Union[float, None] = None) -> 'Actor':
        """
        Set the transform of the actor directly.

        If the actor is spawned, move the actor to the new transform. Only the non-None values will be updated.
        Otherwise, update the initial transform.

        :param x: distance from the origin along the X-axis
        :param y: distance from the origin along the Y-axis
        :param z: distance from the origin along the Z-axis
        :param roll: rotation around the X-axis
        :param pitch: rotation around the Y-axis
        :param yaw: rotation around the Z-axis
        :return: return self for method chaining.
        """
        # select the target transform by checking if the actor is alive
        if self.is_alive():
            target = self.transform
        else:
            target = self.transform_init

        # update the target transform
        if x is not None:
            target.location.x = x
        if y is not None:
            target.location.y = y
        if z is not None:
            target.location.z = z
        if roll is not None:
            target.rotation.roll = roll
        if pitch is not None:
            target.rotation.pitch = pitch
        if yaw is not None:
            target.rotation.yaw = yaw

        # set the target transform
        self.set_transform(target)
        return self

    def use_carla_physics(self, *, option=True) -> 'Actor':
        """
        Enable or disable the carla physics for the actor.

        :param option: True to enable, False to disable.
        :return: return self for method chaining.
        """
        self._option_carla_physics = option
        if self.is_alive():
            self.carla_actor.set_simulate_physics(option)
        return self

    def invoke_bind_carla_actor(self, carla_actor: carla.Actor, *, no_hook=False) -> 'Actor':
        """
        Bind a carla.Actor instance to the actor.

        This method is used internally by the actor manager during spawn.

        :param carla_actor: a carla.Actor instance
        :param no_hook: Optional, if True, skip the hook method on_actor_bind().
        :return: return self for method chaining.
        """
        # health check
        if not isinstance(carla_actor, carla.Actor):
            raise TypeError(f"carla_actor should be a carla.Actor instance, but got {type(carla_actor)}")
        if not carla_actor.is_alive:
            raise RuntimeError(f"carla_actor {carla_actor.id} is not alive. Maybe an extra tick is needed.")
        # invoke banding
        self._carla_actor = carla_actor
        # call hook
        if not no_hook:
            self.on_actor_bind()
        return self

    def invoke_destroy(self, *, no_hook=False) -> 'Actor':
        """
        Destroy the actor.

        :param no_hook: Optional, if True, skip the hook method on_actor_destroy().
        :return: return self for method chaining.
        """
        # call hook
        if not no_hook:
            self.on_actor_destroy()
        # destroy the actor
        if self.is_alive():
            self.carla_actor.destroy()
        self._carla_actor = None
        return self

    def on_actor_bind(self):
        """
        A hook method that will be called after the actor is bound to a carla.Actor instance.

        :return: None
        """
        self.use_carla_physics(option=self._option_carla_physics)
        return

    def on_actor_destroy(self):
        """
        A hook method that will be called before the actor is destroyed.
        :return:
        """
        pass
