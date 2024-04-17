import pickle
import socket
from multiprocessing.connection import Connection
from typing import Optional

from .BaseProxy import BaseProxy
from ..actor import Lidar
from ..core.data import LidarData


class ProxyLidarDataUdp(BaseProxy):
    """
    A proxy class for the GNSS data UDP server.
    """

    def __init__(self,
                 lidar: Lidar,
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
        self._lidar = lidar
        self._target_ip = target_ip
        self._target_port = target_port

    @property
    def lidar(self) -> Lidar:
        """
        [Immutable] The Lidar instance.
        """
        return self._lidar

    @property
    def udp_target(self) -> tuple:
        """
        [Read-Only] The target IP and port of the UDP server.
        """
        return self._target_ip, self._target_port

    def handler_thread_func(self, pipe: Connection):
        while self.is_continue():
            try:
                self.lidar.event_data_update.wait(timeout=self.THREAD_RUNNING_INTERVAL)
                pipe.send(pickle.dumps(self.lidar.data))
            except BrokenPipeError:
                # if the pipe is broken, break the loop without any error
                self._flag_internal_exit = True
                break

    def handler_process_func(self, pipe: Connection):
        in_lidar_data = None  # type: Optional[LidarData]
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # main loop
        while self.is_continue():
            try:
                if pipe.poll(timeout=self.PROCESS_RUNNING_INTERVAL):
                    in_lidar_data = pickle.loads(pipe.recv())
            except KeyboardInterrupt:
                # if press Ctrl+C, KeyboardInterrupt will be raised
                # so break the loop without any error
                break

            if not isinstance(in_lidar_data, LidarData):
                continue

            # create udp data msg
            msg_type = bytes([0x01])
            msg_reserved = bytes([0x00, 0x00, 0x00])
            msg_count = len(in_lidar_data.points).to_bytes(4, byteorder='big', signed=True)

            msg = msg_type + msg_reserved + msg_count

            udp_socket.sendto(msg, self.udp_target)
