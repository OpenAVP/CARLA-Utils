import pickle
import time
import numpy
import sys
import socket
from multiprocessing.connection import Connection
from typing import Optional

from .BaseProxy import BaseProxy
from ..actor import Radar
from ..core.data import RadarData


class ProxyRadarDataUdp(BaseProxy):
    """
    A proxy class for the GNSS data UDP server.
    """

    def __init__(self,
                 radar: Radar,
                 *,
                 target_ip: str,
                 target_port: int,
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
        self._radar = radar
        self._target_ip = target_ip
        self._target_port = target_port

    @property
    def radar(self) -> Radar:
        """
        [Immutable] The GNSS instance.
        """
        return self._radar

    @property
    def udp_target(self) -> tuple:
        """
        [Read-Only] The target IP and port of the UDP server.
        """
        return self._target_ip, self._target_port

    def handler_thread_func(self, pipe: Connection):
        while self.is_continue():
            try:
                self.radar.event_data_update.wait(timeout=self.THREAD_RUNNING_INTERVAL)
                pipe.send(pickle.dumps(self.radar.data))
            except BrokenPipeError:
                # if the pipe is broken, break the loop without any error
                self._flag_internal_exit = True
                break

    def handler_process_func(self, pipe: Connection):
        in_radar_data = None  # type: Optional[RadarData]
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # main loop
        while self.is_continue():
            try:
                if pipe.poll(timeout=self.PROCESS_RUNNING_INTERVAL):
                    in_radar_data = pickle.loads(pipe.recv())
            except KeyboardInterrupt:
                # if press Ctrl+C, KeyboardInterrupt will be raised
                # so break the loop without any error
                break

            if not isinstance(in_radar_data, RadarData):
                continue

            # create udp data msg
            msg_type = bytes([0x01])
            msg_reserved = bytes([0x00, 0x00, 0x00])
            msg_count = len(in_radar_data.points).to_bytes(4, byteorder='big', signed=True)

            msg = msg_type + msg_reserved + msg_count

            d = []
            for p in in_radar_data.points:
                d.append([p.altitude, p.azimuth, p.depth, p.velocity])
            d = numpy.array(d).reshape(-1, 4)

            x = d[:, 2] * numpy.cos(d[:, 1]) * numpy.cos(-d[:, 0])
            y = d[:, 2] * numpy.sin(-d[:, 1]) * numpy.cos(d[:, 0])
            vx = d[:, 3] * numpy.cos(d[:, 1]) * numpy.cos(-d[:, 0])
            vy = d[:, 3] * numpy.sin(-d[:, 1]) * numpy.cos(d[:, 0])

            pts = numpy.column_stack((x, y, vx, vy))

            data = pts.astype(numpy.float32)
            if sys.byteorder == 'little':
                data = data.byteswap()

            for i, p in enumerate(data):
                msg_id = i.to_bytes(4, byteorder='big', signed=True)
                msg_points = p.tobytes()
                msg = msg + msg_id + msg_points

            udp_socket.sendto(msg, self.udp_target)
