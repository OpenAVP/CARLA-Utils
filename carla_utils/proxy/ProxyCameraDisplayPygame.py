import pickle
import pygame
import numpy
from multiprocessing.connection import Connection

from ..actor import Camera
from ..core.data import ImageData
from .BaseProxy import BaseProxy


class ProxyCameraDisplayPygame(BaseProxy):

    def __init__(self,
                 camera: Camera,
                 *,
                 name: str = None,
                 fullscreen: bool = False,
                 screen: int = 0,
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
        self._camera = camera
        self._fullscreen = fullscreen
        self._screen = screen

    @property
    def camera(self) -> Camera:
        """
        [Immutable] The camera instance.
        :return:
        """
        return self._camera

    @property
    def source_size(self) -> tuple:
        """
        [Immutable] The size of the source image. (width/x, height/y)
        :return:
        """
        return int(self.camera.attributes.get('image_size_x')), int(self.camera.attributes.get('image_size_y'))

    @property
    def fullscreen(self) -> bool:
        """
        [Read-only] Dose the pygame window is fullscreen.
        """
        return self._fullscreen

    @property
    def screen(self) -> int:
        """
        [Read-only] The screen number to put pygame window.
        """
        return self._screen

    def handler_process_func(self, pipe: Connection):
        # setup pygame
        pygame.init()
        pygame.display.set_caption(self.name)

        # find the match window size
        try:
            pygame_window_mode = pygame.display.list_modes(0, pygame.FULLSCREEN, self.screen)
        except ValueError:
            # ValueError occurs when the screen number is out of range, use 0 for default
            # If there is still no match, maybe no screen is connected, it should raise an error
            pygame_window_mode = pygame.display.list_modes(0, pygame.FULLSCREEN, 0)

        # setup pygame window
        pygame_window_size = pygame_window_mode[0] if self.fullscreen else self.source_size
        pygame_window = pygame.display.set_mode(pygame_window_mode[0] if self.fullscreen else self.source_size,
                                                pygame.FULLSCREEN if self.fullscreen else 0,
                                                self.screen)

        # create a new debug texture
        debug_texture = self._new_debug_texture(*pygame_window_size)
        surface = pygame.surfarray.make_surface(debug_texture.swapaxes(0, 1))

        # main loop
        while self.is_continue():
            # exit if pipe is closed
            if pipe.closed:
                break

            # exit if press Ctrl+C, ESC or close pygame window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._flag_internal_exit = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self._flag_internal_exit = True
                    if event.key == pygame.K_c and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self._flag_internal_exit = True

            # show image
            try:
                if pipe.poll(timeout=self.D_PROCESS_RUNNING_INTERVAL):
                    in_image_data = pickle.loads(pipe.recv())
                    if isinstance(in_image_data, ImageData):
                        surface = pygame.surfarray.make_surface(in_image_data.as_pygame_surface_data())
            except KeyboardInterrupt:
                # if press Ctrl+C, KeyboardInterrupt will be raised
                # so break the loop without any error
                break

            # update
            pygame_window.blit(surface, (0, 0))
            pygame.display.flip()

    @staticmethod
    def _new_debug_texture(width, height) -> numpy.ndarray:
        """
        Create a new debug texture.
        :param width: texture width
        :param height: texture height
        :return:
        """
        texture = numpy.zeros((width, height, 3), dtype=numpy.uint8)
        for i in range(0, texture.shape[0], 16):
            for j in range(0, texture.shape[1], 16):
                color = numpy.random.randint(0, 255, (3), dtype=numpy.uint8)
                texture[i:i + 128, j:j + 128] = color

        texture = texture[:, :, ::-1]
        texture = texture.swapaxes(0, 1)
        return texture

    def handler_thread_func(self, pipe: Connection):
        while self.is_continue():
            # exit if pipe is closed
            if pipe.closed:
                break

            # get image from camera
            self.camera.event_data_update.wait(timeout=self.THREAD_RUNNING_INTERVAL)
            send_data = pickle.dumps(self.camera.data)
            try:
                pipe.send(send_data)
            except BrokenPipeError:
                # if process is closed, BrokenPipeError will be raised
                # so break the loop
                break
