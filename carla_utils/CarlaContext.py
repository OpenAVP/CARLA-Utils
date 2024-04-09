import time
import signal
import carla
from typing import Union, List

from .manager import RunningManager, ActorManager


class CarlaContext:

    def __init__(self,
                 host: str = '127.0.0.1',
                 port: int = 2000,
                 timeout: float = 2.0):
        # basic
        self._host = host
        self._port = port
        self.timeout = timeout
        # carla
        self._carla_client = None  # type: Union[carla.Client, None]
        self._carla_world_ref = [None]  # type: List[Union[carla.World, None]]  # mutable reference, len===1
        # flags
        self._flag_internal_exit = False
        # managers
        self.actors = ActorManager(self.carla_world_ref)
        self.running = RunningManager(self.carla_world_ref)

    def __del__(self):
        self.invoke_connection_stop()

    def __enter__(self):
        return self.invoke_connection_start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.invoke_connection_stop()

    @property
    def host(self) -> str:
        """
        [Read-Only] Get the host set in the context
        """
        return self._host

    @property
    def port(self) -> int:
        """
        [Read-Only] Get the port set in the context
        """
        return self._port

    @property
    def carla_client(self) -> carla.Client:
        """
        [Immutable] Get the carla client
        """
        return self._carla_client

    @property
    def carla_world(self) -> carla.World:
        """
        [Immutable] Get the carla client
        """
        self._update_carla_world_ref()
        return self._carla_world_ref[0]

    @property
    def carla_world_ref(self) -> List[Union[carla.World, None]]:
        """
        [Immutable] Get the carla world reference with 1 element list.
        """
        self._update_carla_world_ref()
        return self._carla_world_ref

    def is_alive(self, *, raise_exception: bool = False) -> bool:
        """
        Check that the carla client connection in CarlaContext is good.
        :param raise_exception: whether to raise exceptions if check failed.
        :return: check result
        :except ConnectionError: if raise_exception is True and connection check failed.
        """
        if not isinstance(self.carla_client, carla.Client):
            return False
        try:
            # try to get carla server version
            self.carla_client.get_server_version()
            self._update_carla_world_ref()
        except RuntimeError as e:
            # RuntimeError means that connection is not good, raise exceptions on request.
            if raise_exception:
                raise ConnectionError(e) from e
            else:
                return False
        else:
            # if no exceptions happened
            return True

    def use_map(self, map_name: str) -> 'CarlaContext':
        """
        Change carla server map.
        This operation has effect same as `reload_world` method.

        :param map_name: carla map name registered on server
        :return: return self for method chaining.
        :except ConnectionError: if connection check failed.
        :except RuntimeError: if map_name is not a valid carla map name.
        """
        self.is_alive(raise_exception=True)
        self.carla_client.load_world(map_name)
        return self

    def reload_world(self, reset_settings: bool = False) -> 'CarlaContext':
        """
        Reload carla world in server.

        [ ! ] All actors will be cleand in current context.
        :return: return self for method chaining.
        """
        self.is_alive(raise_exception=True)
        self.carla_client.reload_world(reset_settings=reset_settings)
        return self

    def wait_for_ticks(self, count: int = 1, timeout: float = 0.0) -> 'CarlaContext':
        """
        Wait for server to tick for a certain amount of times.
        :param timeout: the maximum time to wait for all ticks. 0 means no timeout.
        :param count: tick count to wait
        :return: return self for method chaining.
        """
        time_start = time.time()
        for _ in range(count):
            if timeout > 0:
                time_left = timeout - (time.time() - time_start)
            else:
                time_left = None
            if self.running.event_carla_tick.wait(timeout=time_left):
                continue
            else:
                raise TimeoutError(f'Timeout waiting for {count} ticks.')
        return self

    def wait_for_seconds(self, seconds: float) -> 'CarlaContext':
        """
        Wait for seconds to let server do some work.
        :param seconds: seconds to wait
        :return: return self for method chaining.
        """
        time.sleep(seconds)
        return self

    def invoke_hold(self):
        """
        Hold the context to prevent it from being closed.

        It must the last method to be called in the main thread.
        """
        def signal_handler(signum, frame):
            """
            Signal handler to let the hold exit safely.
            :param signum: not used
            :param frame: not used
            :return: None
            """
            self._flag_internal_exit = True

        # register signal handler to prevent the program from exiting
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # hold the context
        # note that KeyboardInterrupt will be caught by signal handler
        while self._flag_internal_exit is False:
            time.sleep(0.1)  # sleep for a while to prevent high CPU usage
            print('Alive. Press Ctrl+C to exit.')

    def invoke_connection_start(self) -> 'CarlaContext':
        """
        Connect to carla server.
        :return: return self for method chaining.
        """
        # directly return if already connected
        if self.is_alive():
            return self
        # create carla client
        self._carla_client = carla.Client(self.host, self.port)
        self.carla_client.set_timeout(self.timeout)
        # test connection
        try:
            self.is_alive(raise_exception=True)
        except ConnectionError as e:
            self._carla_client = None
            raise e
        # and return
        return self

    def invoke_connection_stop(self) -> 'CarlaContext':
        """
        Disconnect from carla server.
        """
        if not self.is_alive():
            return self
        self.running.use_sync_primary_mode(False)
        self.actors.invoke_actor_destroy(self.actors.registry)
        self.wait_for_ticks(5, timeout=2.0)
        # release client
        self._carla_client = None
        return self

    def _update_carla_world_ref(self):
        """
        Update the carla world reference.

        This method is called before accessing the carla world.
        Do not call this method directly.
        """
        if not self.is_alive():
            self._carla_world_ref[0] = None
        try:
            self._carla_world_ref[0] = self.carla_client.get_world()
        except (RuntimeError, ConnectionError, AttributeError):
            self._carla_world_ref[0] = None
