import time
import pickle
import pygame

from .BaseProxy import BaseProxy
from ..actor import Vehicle
from ..core.data import VehicleStatusData
from ..core.cmd import VehicleDirectControlCmd


class ProxyVehicleKeyboardControlPygame(BaseProxy):
    """
    A vehicle keyboard control proxy based on Pygame.
    """

    def __init__(self,
                 vehicle: Vehicle,
                 *,
                 name: str = None,
                 process_join_timeout: float = BaseProxy.D_PROCESS_JOIN_TIMEOUT,
                 process_running_interval: float = BaseProxy.D_PROCESS_RUNNING_INTERVAL,
                 thread_join_timeout: float = BaseProxy.D_THREAD_JOIN_TIMEOUT,
                 thread_running_interval: float = BaseProxy.D_THREAD_RUNNING_INTERVAL):
        super().__init__(
            name=name,
            process_join_timeout=process_join_timeout,
            process_running_interval=process_running_interval,
            thread_join_timeout=thread_join_timeout,
            thread_running_interval=thread_running_interval
        )
        if not isinstance(vehicle, Vehicle):
            raise TypeError(f"vehicle must be an instance of Vehicle, got {type(vehicle)} instead.")
        self._vehicle = vehicle

    @property
    def vehicle(self) -> Vehicle:
        """
        [Immutable] The vehicle object that this proxy is controlling.
        :return: Vehicle instance.
        """
        return self._vehicle

    def handler_thread_func(self, pipe):
        """
        In thread function, the proxy will do the following things:

        - Listen to the pipe waiting for the VehicleDirectControlCmd from the Process.
        - Get vehicle status data and send them to the Process with VehicleStatusData via Pipe.

        :param pipe: A Pipe object that connects the Process and the Thread.
        :return: None
        """
        in_vdcc = None

        while self.is_continue():
            # exit if pipe is closed
            if pipe.closed:
                break

            # exit if process is not alive
            if not (self.handler_process and self.handler_process.is_alive()):
                break

            # empty loop if vehicle is not alive
            if not (self.vehicle and self.vehicle.is_alive()):
                time.sleep(0.1)
                continue

            # handle the VehicleDirectControlCmd input
            if isinstance(in_vdcc, VehicleDirectControlCmd):
                self.vehicle.invoke_direct_control(in_vdcc)

            # update the VehicleStatusData output
            out_vsd = self.vehicle.status

            # recv and send data
            try:
                if pipe.poll(self.THREAD_RUNNING_INTERVAL):
                    in_vdcc = pickle.loads(pipe.recv())
                pipe.send(pickle.dumps(out_vsd))  # send interval is basically equal to self.THREAD_RUNNING_INTERVAL
            except ConnectionResetError:
                # if the pipe is closed, break the loop
                self._flag_internal_exit = True
                break

            # end loop
            continue

    def handler_process_func(self, pipe):
        """
        In thread function, the proxy will do the following things:

        - Handler the user input from the keyboard.
          Load them to the VehicleDirectControlCmd and send them to the Thread via Pipe.
        - Listen to the pipe waiting for the VehicleStatusData from the Thread.
          Display the vehicle status data to the user.

        :param pipe: A Pipe object that connects the Process and the Thread.
        :return: None
        """
        # init pygame settings
        pygame.init()
        pygame.key.set_repeat(0, 300)
        pygame_window = pygame.display.set_mode(size=(400, 300))
        pygame_font = pygame.font.SysFont('Console', size=16, bold=True)
        pygame_clock = pygame.time.Clock()

        # cached objects
        out_vdcc = VehicleDirectControlCmd()
        in_vsd = VehicleStatusData()

        # message header
        msg_header_throttle = 'Throttle:'.ljust(12, ' ')
        msg_header_brake = 'Brake:'.ljust(12, ' ')
        msg_header_steer = 'Steer:'.ljust(12, ' ')
        msg_header_handbrake = 'Handbrake:'.ljust(12, ' ')
        msg_header_reverse = 'Reverse:'.ljust(12, ' ')
        msg_header_speed_mps = 'Speed(m/s):'.ljust(15, ' ')
        msg_header_speed_kmph = 'Speed(km/h):'.ljust(15, ' ')

        # main loop
        while self.is_continue():
            # exit if pipe is closed
            if pipe.closed:
                break

            # control pygame tick
            try:
                pygame_clock.tick(1 / self.PROCESS_RUNNING_INTERVAL)
            except KeyboardInterrupt:
                # exit if KeyboardInterrupt
                break

            # handler pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._flag_internal_exit = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        out_vdcc.throttle = min(out_vdcc.throttle + 0.1, 1)
                        out_vdcc.brake = 0.0
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        out_vdcc.brake = min(out_vdcc.brake + 0.1, 1)
                        out_vdcc.throttle = 0.0
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        out_vdcc.steer = max(out_vdcc.steer - 0.1, -1)
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        out_vdcc.steer = min(out_vdcc.steer + 0.1, 1)
                    if event.key == pygame.K_SPACE:
                        out_vdcc.hand_brake = not out_vdcc.hand_brake
                    if event.key == pygame.K_r:
                        out_vdcc.reverse = not out_vdcc.reverse

            # send & recv data
            pipe.send(pickle.dumps(out_vdcc))
            while pipe.poll():
                in_vsd = pickle.loads(pipe.recv())
                if not isinstance(in_vsd, VehicleStatusData):
                    raise TypeError(f'Received data is not VehicleStatusData, got {type(in_vsd)} instead.')

            msg_speed_mps = msg_header_speed_mps + (
                str(round(in_vsd.speed, 1)) if in_vsd and in_vsd.speed is not None else '[NO-DATA]')
            msg_speed_kmph = msg_header_speed_kmph + (
                str(round(in_vsd.speed * 3.6, 1)) if in_vsd and in_vsd.speed is not None else '[NO-DATA]')
            msg_throttle = msg_header_throttle + (
                str(round(in_vsd.throttle * 100)) + '%' if in_vsd and in_vsd.throttle is not None else '[NO-DATA]')
            msg_brake = msg_header_brake + (
                str(round(in_vsd.brake * 100)) + '%' if in_vsd and in_vsd.brake is not None else '[NO-DATA]')
            msg_steer = msg_header_steer + (
                str(round(in_vsd.steer * 100)) + '%' if in_vsd and in_vsd.steer is not None else '[NO-DATA]')
            msg_handbrake = msg_header_handbrake + (
                str(in_vsd.hand_brake) if in_vsd and in_vsd.hand_brake is not None else '[NO-DATA]')
            msg_reverse = msg_header_reverse + (
                str(in_vsd.reverse) if in_vsd and in_vsd.reverse is not None else '[NO-DATA]')

            # render
            pygame_window.fill((20, 24, 41))  # in R, G, B

            text_throttle = pygame_font.render(msg_throttle, False, (255, 255, 255))
            text_brake = pygame_font.render(msg_brake, False, (255, 255, 255))
            text_steer = pygame_font.render(msg_steer, False, (255, 255, 255))
            text_handbrake = pygame_font.render(msg_handbrake, False, (255, 255, 255))
            text_reverse = pygame_font.render(msg_reverse, False, (255, 255, 255))
            text_speed_mps = pygame_font.render(msg_speed_mps, False, (255, 255, 255))
            text_speed_kmph = pygame_font.render(msg_speed_kmph, False, (255, 255, 255))
            text_line = pygame_font.render('-' * 30, False, (255, 255, 255))

            pygame_window.blit(text_throttle, text_throttle.get_rect(topleft=(10, 10)))
            pygame_window.blit(text_brake, text_brake.get_rect(topleft=(10, 30)))
            pygame_window.blit(text_steer, text_steer.get_rect(topleft=(10, 50)))
            pygame_window.blit(text_handbrake, text_handbrake.get_rect(topleft=(10, 70)))
            pygame_window.blit(text_reverse, text_reverse.get_rect(topleft=(10, 90)))
            pygame_window.blit(text_line, text_line.get_rect(topleft=(10, 110)))
            pygame_window.blit(text_speed_mps, text_speed_mps.get_rect(topleft=(10, 130)))
            pygame_window.blit(text_speed_kmph, text_speed_kmph.get_rect(topleft=(10, 150)))

            # update pygame
            pygame.display.flip()
