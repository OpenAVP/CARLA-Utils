import carla
from typing import List, Union, Set

from carla_utils.actor import Actor, Vehicle, Sensor


class ActorManager:
    """
    A class to manage the actors life-cycles in the CARLA simulator
    """

    def __init__(self, world_ref: List[carla.World]):
        """
        Construct a new ActorManager instance

        This instance should create after CarlaContext created a connection.

        :param world_ref: A len(1) list that contains the nullable carla.World instance.
        """
        self._carla_world_ref = world_ref
        self._registry = set()  # type: Set[Actor]

    def __del__(self):
        # destroy all actors in registry when ActorManager exit.
        self.invoke_actor_destroy(self.registry)

    @property
    def carla_world(self) -> carla.World:
        """
        [Immutable] The carla.World instance that ActorManager operates on
        """
        return self._carla_world_ref[0]

    @property
    def registry(self) -> Set[Actor]:
        """
        [Immutable] A list of actors that are managed by this ActorManager

        Once an actor is known by the ActorManager, it will be hold in actor registry until ActorManager is destroyed.
        """
        return self._registry

    def new_actor(self, blueprint_name: str, *, parent: Union[None, Actor] = None) -> Actor:
        """
        Create a new actor instance.

        :param parent: parent Actor instance
        :param blueprint_name: blueprint name str defined in carla.BlueprintLibrary
        :return: Actor instance
        """
        actor = Actor(blueprint_name)
        self._registry.add(actor)
        if parent:
            actor.set_parent(parent)
        return actor

    def new_vehicle(self, blueprint_name: str, *, parent: Union[None, Actor] = None) -> Vehicle:
        """
        Create a new vehicle instance.

        :param parent: parent Actor instance
        :param blueprint_name: blueprint name str defined in carla.BlueprintLibrary
        :return: Vehicle instance
        """
        actor = Vehicle(blueprint_name)
        self._registry.add(actor)
        if parent:
            actor.set_parent(parent)
        return actor

    def new_sensor(self, blueprint_name: str, *, parent: Union[None, Actor] = None) -> Sensor:
        """
        Create a new sensor instance.

        :param parent: parent Actor instance
        :param blueprint_name: blueprint name str defined in carla.BlueprintLibrary
        :return: Sensor instance
        """
        actor = Sensor(blueprint_name)
        self._registry.add(actor)
        if parent:
            actor.set_parent(parent)
        return actor

    def invoke_actor_spawn(self, actor: Union[Actor, List[Actor], Set[Actor]]) -> 'ActorManager':
        """
        Spawn actor(s) in the simulator

        :param actor: a single, list or set of Actor instances to spawn
        :return: return self for method chaining.
        :raises RuntimeError: if any actor fails to spawn
        """
        # input clean
        if isinstance(actor, Actor):
            actors = [actor]
        elif isinstance(actor, list):
            actors = actor.copy()
        elif isinstance(actor, set):
            actors = list(actor)
        else:
            raise TypeError(f'A list of Actor or Actor instance is expected, but got {type(actor)}')

        # spawn and bind
        spawn_exceptions = list()
        for a in actors:
            attach_target = a.parent.carla_actor if a.parent else None
            try:
                carla_actor = self.carla_world.spawn_actor(blueprint=a.blueprint.as_carla_blueprint(self.carla_world),
                                                           transform=a.transform.as_carla_transform(),
                                                           attach_to=attach_target)
                self.carla_world.wait_for_tick() # wait for the actor to be spawned
                a.invoke_bind_carla_actor(carla_actor)
                self.registry.add(a)  # idempotent operation, duplicate additions will be ignored
            except RuntimeError as e:
                spawn_exceptions.append(e)
                continue
        if spawn_exceptions:
            error_msg = f'Failed to spawn {len(spawn_exceptions)} actor(s):\n'
            for e in spawn_exceptions:
                error_msg += f'\t{e}\n'
            raise RuntimeError(error_msg)
        # and return
        return self

    def invoke_actor_destroy(self, actor: Union[Actor, List[Actor], Set[Actor]]) -> 'ActorManager':
        """
        Destroy actor(s) in the simulator

        :param actor: a single, list or set of Actor instances to spawn
        :return: return self for method chaining.
        """
        # input clean
        actors = []
        if isinstance(actor, Actor):
            actors = [actor]
        elif isinstance(actor, set):
            actors = list(actor)
        elif isinstance(actor, list):
            actors = actor.copy()

        for a in actors:
            if a.is_alive():
                a.invoke_destroy()
            # actor will not be removed from registry until ActorManger is destroyed

        return self
