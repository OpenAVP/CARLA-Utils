import uuid
from threading import Thread
from multiprocessing import Process, Pipe
from multiprocessing.connection import Connection
from abc import ABC, abstractmethod


class BaseProxy(ABC):
    """
    Proxy is designed to send or receive data from an external source and communicate with the CarlaContext.
    The external source can be everything defined by the user, such as a ROS Node, UDP socket, etc.

    There is a thread and a process in a proxy:

    - Thread: It is used to handle the communication with the CarlaContext source in a single GIL.
      All operations on the CarlaContext should be implemented in-thread.

    - Process: It is used to handle the communication with the external source in a separate process.
      It will maximize the use of multiple CPUs and avoid blocking the CarlaContext.
      IO and data post-processing should be implemented in the Process.

    Thread and Process communicate with each other through a PIPE.

    Process can be disabled by setting USE_PROCESS to False for using a lighter weight proxy.

    """

    D_PROCESS_JOIN_TIMEOUT = 2.0  # in seconds
    D_PROCESS_RUNNING_INTERVAL = 0.01  # in seconds
    D_THREAD_JOIN_TIMEOUT = 2.0  # in seconds
    D_THREAD_RUNNING_INTERVAL = 0.01  # in seconds

    USE_PROCESS = True  # you can disable process for lightweight proxies

    def __init__(self, *,
                 name: str = None,
                 process_join_timeout: float = D_PROCESS_JOIN_TIMEOUT,
                 process_running_interval: float = D_PROCESS_RUNNING_INTERVAL,
                 thread_join_timeout: float = D_THREAD_JOIN_TIMEOUT,
                 thread_running_interval: float = D_THREAD_RUNNING_INTERVAL):
        """
        Construct a new BaseProxy object.
        :param name: Name of the proxy. If not set, it will return the class name and the first 8 characters of the ID.
        """
        # basic
        self._id = uuid.uuid4()
        self._name = name
        self._process_join_timeout = process_join_timeout
        self._process_running_interval = process_running_interval
        self._thread_join_timeout = thread_join_timeout
        self._thread_running_interval = thread_running_interval
        # handler
        self._handler_thread = None  # Union[Thread, Process]
        self._handler_process = None  # Union[Thread, Process]
        # flags
        self._flag_internal_exit = False

    @property
    def id(self) -> str:
        """
        ID of the proxy. in the form of a UUID 4.
        :return: str
        """
        return str(self._id)

    @property
    def name(self) -> str:
        """
        Name of the proxy. If not set, it will return the class name and the first 8 characters of the ID.
        :return: str
        """
        if self._name:
            return self._name
        return f'{self.__class__.__name__}-{self.id[:8]}'

    @property
    def handler_process(self) -> Process:
        return self._handler_process

    @property
    def handler_thread(self) -> Thread:
        return self._handler_thread

    @property
    def PROCESS_JOIN_TIMEOUT(self) -> float:
        """
        [Read-Only] Process join timeout in seconds.
        """
        return self._process_join_timeout

    @property
    def PROCESS_RUNNING_INTERVAL(self) -> float:
        """
        [Read-Only] Expected Value. Process running interval in seconds. 100Hz == 0.01s
        """
        return self._process_running_interval

    @property
    def THEAD_JOIN_TIMEOUT(self) -> float:
        """
        [Read-Only] Thread join timeout in seconds.
        """
        return self._thread_join_timeout

    @property
    def THEAD_RUNNING_INTERVAL(self) -> float:
        """
        [Read-Only] Expected Value. Thread running interval in seconds. 100Hz == 0.01s
        """
        return self._thread_running_interval

    def is_continue(self) -> bool:
        return not self._flag_internal_exit

    def invoke_start(self) -> 'BaseProxy':
        if self.USE_PROCESS:
            pipe_end_1, pipe_end_2 = Pipe()
            self._handler_thread = Thread(target=self.handler_thread_func,
                                          name=self.name + '-T',
                                          args=(pipe_end_1,),
                                          daemon=True)
            self._handler_process = Process(target=self.handler_process_func,
                                            name=self.name + '-P',
                                            args=(pipe_end_2,),
                                            daemon=True)
            self.handler_thread.start()
            self.handler_process.start()
        else:
            self._handler_thread = Thread(target=self.handler_thread_func,
                                          name=self.name + '-T',
                                          daemon=True)
            self.handler_thread.start()
        return self

    def invoke_stop(self) -> 'BaseProxy':
        self._flag_internal_exit = True

        if self.handler_process and self.handler_process.is_alive():
            self.handler_process.join(timeout=self.PROCESS_JOIN_TIMEOUT)
            self.handler_process.terminate()
        if self.handler_thread and self.handler_thread.is_alive():
            self.handler_thread.join(timeout=self.THEAD_JOIN_TIMEOUT)

        self._handler_process = None
        self._handler_process = None
        return self

    @abstractmethod
    def handler_process_func(self, pipe: Connection):
        pass

    @abstractmethod
    def handler_thread_func(self, pipe: Connection):
        pass
