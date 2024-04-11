import pickle
import time
import numpy
import sys
import socket
from multiprocessing.connection import Connection
from typing import Optional

from .BaseProxy import BaseProxy
from ..actor import Gnss
from ..core.data import GnssData


class ProxyGnssDataUdp(BaseProxy):
    """
    A proxy class for the GNSS data UDP server.
    """

    def __init__(self,
                 gnss: Gnss,
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
        self._gnss = gnss
        self._target_ip = target_ip
        self._target_port = target_port

    @property
    def imu(self) -> Gnss:
        """
        [Immutable] The IMU instance.
        """
        return self._gnss

    @property
    def udp_target(self) -> tuple:
        """
        [Read-Only] The target IP and port of the UDP server.
        """
        return self._target_ip, self._target_port

    def handler_thread_func(self, pipe: Connection):
        while self.is_continue():
            try:
                pipe.send(pickle.dumps(self.imu.data))
            except BrokenPipeError:
                # if the pipe is broken, break the loop without any error
                self._flag_internal_exit = True
                break
            time.sleep(self.THREAD_RUNNING_INTERVAL)

    def handler_process_func(self, pipe: Connection):
        in_gnss_data = None  # type: Optional[GnssData]
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # main loop
        while self.is_continue():
            try:
                if pipe.poll(timeout=self.PROCESS_RUNNING_INTERVAL):
                    in_gnss_data = pickle.loads(pipe.recv())
            except KeyboardInterrupt:
                # if press Ctrl+C, KeyboardInterrupt will be raised
                # so break the loop without any error
                break

            if not isinstance(in_gnss_data, GnssData):
                continue

            # create udp data msg
            msg_type = bytes([0x02])
            msg_reserved = bytes([0x00, 0x00, 0x00])
            msg_data = numpy.array([
                in_gnss_data.latitude,
                in_gnss_data.longitude,
                in_gnss_data.altitude,
            ])
            msg_data = msg_data.astype(numpy.float32)

            if sys.byteorder == 'little':
                msg_data = msg_data.byteswap()

            msg = msg_type + msg_reserved + msg_data.tobytes()
            udp_socket.sendto(msg, self.udp_target)
