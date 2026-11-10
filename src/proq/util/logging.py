import time
from collections.abc import Callable

LogMethod = Callable[[str], None]

class Logger:
    setup: LogMethod
    memory: LogMethod
    register: LogMethod
    clock: LogMethod
    cu: LogMethod
    alu: LogMethod
    interrupt: LogMethod
    stdout: LogMethod
    modes: LogMethod
    stack: LogMethod

    start_time = time.perf_counter()

    def __init__(self, default: bool = False, **kwargs: bool) -> None:
        self.log_types: dict[str, bool] = {}

        for name in type(self).__annotations__:
            enabled = kwargs.get(name, default)
            self.log_types[name] = enabled
            setattr(self, name, self._make_logger(name))

    def _make_logger(self, name: str) -> LogMethod:
        def _log(message: str) -> None:
            if self.log_types[name]:
                print(f"{time.perf_counter() - self.start_time:.6f} [{name.upper()}]: {message}")
        return _log
