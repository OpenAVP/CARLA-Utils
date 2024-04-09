import carla
import time
from threading import Thread, Event
from typing import Union, List


class RunningManager:
    """
    A class that manages the running of the CARLA simulation.

    Mainly for simulation sync, async control.
    """

    def __init__(self, world_ref: List[carla.World]):
        """
        Construct a RunningManager instance.

        This instance should create after CarlaContext created a connection.

        :param world_ref: A len(1) list that contains the nullable carla.World instance.
        """
        self._carla_world_ref = world_ref
        self._event_carla_tick = Event()
        # time
        self._time_simulation_begin = 0.0
        self._time_realworld_begin = 0.0
        # sync options
        self._option_sync_primary_mode = False
        self._option_strict_time_mode = False
        self._sync_fixed_delta_time = 0.0  # in seconds
        # flags
        self._flag_internal_exit = False
        # running control
        self._control_thread = Thread(target=self._control_thread_func, daemon=True)
        self._control_thread.start()

    def __del__(self):
        # release sync primary mode when object deleted
        self.use_sync_primary_mode(False)
        self._flag_internal_exit = True
        self._control_thread.join(1)

    @property
    def carla_world(self) -> carla.World:
        """
        [Immutable] The carla.World instance that RunningManager operates on
        """
        return self._carla_world_ref[0]

    @property
    def event_carla_tick(self) -> Event:
        """
        [Immutable] The event that is set when a new tick is received from CARLA
        """
        return self._event_carla_tick

    @property
    def time_simulation_begin(self) -> float:
        """
        [Read-Only] The linux timestamp when the RunningManager control thread started.
        """
        return self._time_simulation_begin

    @property
    def time_realworld_begin(self) -> float:
        """
        [Read-Only] The linux timestamp when the RunningManager control thread started.
        """
        return self._time_realworld_begin

    @property
    def timespan_simulation(self) -> float:
        """
        [Read-Only] Then time span since the RunningManager control thread started.
        """
        snap = self.carla_world.get_snapshot()
        return snap.timestamp.elapsed_seconds - self.time_simulation_begin

    @property
    def timespan_realworld(self) -> float:
        """
        [Read-Only] Then time span since the RunningManager control thread started.
        """
        return time.time() - self.time_realworld_begin

    @property
    def timespan_realworld_simulation_diff(self) -> float:
        """
        [Read-Only] The difference between the real-world timespan and the simulation timespan.
        """
        return self.timespan_realworld - self.timespan_simulation

    @property
    def option_sync_primary_mode(self) -> bool:
        """
        [Read-Write] Whether the RunningManager is in sync primary mode.
        """
        return self._option_sync_primary_mode

    @property
    def option_strict_time_mode(self) -> bool:
        """
        [Read-Write] Whether the RunningManager is in strict time mode.
        """
        return self._option_strict_time_mode

    @property
    def sync_fixed_delta_time(self) -> float:
        """
        [Read-Write] The fixed delta time for the simulation.
        """
        return self._sync_fixed_delta_time

    def use_sync_primary_mode(self, option: bool, *,
                              fixed_delta_time: float = 0.0,
                              strict_time_mode: bool = False) -> 'RunningManager':
        """
        Enable or disable the sync primary mode.

        This method will not enter strict time mode immediately. Control thread is going to do that.

        :param strict_time_mode: enable or disable the strict time mode.
        :param fixed_delta_time: fixed delta time in seconds.
        :param option: enable or disable the sync primary mode.
        :return: return self for method chaining.
        """
        self._option_sync_primary_mode = option
        # set fixed delta time
        if option:
            if fixed_delta_time <= 0.0:
                raise ValueError("Fixed delta time must be greater than 0 when enabling sync primary mode.")
            self._sync_fixed_delta_time = fixed_delta_time
        # set strict time mode
        self._option_strict_time_mode = strict_time_mode
        return self

    def _invoke_enter_sync_primary_mode(self, fixed_delta_time: float):
        """
        Enter the sync primary mode.
        :param fixed_delta_time: in seconds
        :return: None
        """
        settings = self.carla_world.get_settings()   # type: carla.WorldSettings
        settings.fixed_delta_seconds = fixed_delta_time
        settings.synchronous_mode = True
        self.carla_world.apply_settings(settings)

    def _invoke_exit_sync_primary_mode(self):
        """
        Exit the sync primary mode.
        :return: None
        """
        settings = self.carla_world.get_settings()   # type: carla.WorldSettings
        settings.synchronous_mode = False
        self.carla_world.apply_settings(settings)

    def _control_thread_func(self):
        while self._flag_internal_exit is False:
            # handle world statement
            if self.carla_world is None:
                # reset time if lose world
                if self.time_realworld_begin != 0.0 or self.time_simulation_begin != 0.0:
                    self._time_realworld_begin = 0.0
                    self._time_simulation_begin = 0.0
                # wait for 0.1 seconds to reduce CPU usage
                time.sleep(0.1)
                continue
            elif self.time_realworld_begin == 0.0 and self.time_simulation_begin == 0.0:
                # set time if world created
                self._time_realworld_begin = time.time()
                self._time_simulation_begin = self.carla_world.get_snapshot().timestamp.elapsed_seconds

            # handle sync model change
            if self.option_sync_primary_mode:
                self._invoke_enter_sync_primary_mode(self.sync_fixed_delta_time)
            else:
                self._invoke_exit_sync_primary_mode()

            # calculate client wait time for sync primary mode
            client_wait_time = self.sync_fixed_delta_time
            if self.option_strict_time_mode:
                client_wait_time = self._sync_fixed_delta_time - self.timespan_realworld_simulation_diff
                if client_wait_time <= self._sync_fixed_delta_time * 0.1:
                    client_wait_time = self._sync_fixed_delta_time * 0.1

            # control
            try:
                if self.option_sync_primary_mode:
                    time.sleep(client_wait_time)
                    self.carla_world.tick()
                else:
                    self.carla_world.wait_for_tick()
            except AttributeError:
                # occurred AttributeError means the world is destroyed during process
                # it will be handled safely in the next loop
                pass

            # flash event
            self.event_carla_tick.set()
            self.event_carla_tick.clear()
