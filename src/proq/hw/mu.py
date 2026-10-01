import bisect

from proq.util.exceptions import EmulatorMemoryError
from proq.util.logging import Logger
from proq.util.util import hex

log: Logger

class MemoryDevice:
    def read(self, addr: int) -> int:
        raise NotImplementedError("this memory device does not have anything to read!")
    def write(self, addr: int, value: int):
        raise NotImplementedError("this memory device does not have anything to write!")

class ROM(MemoryDevice):
    def __init__(self, size: int, binary: bytes):
        if len(binary) > size:
            raise EmulatorMemoryError(f"Binary is {len(binary)} bytes, which will not fit in a {size}B ROM")

        self.data = bytearray(size)
        self.data[:len(binary)] = binary

    def read(self, addr: int) -> int:
        return self.data[addr]

    def write(self, addr: int, value: int):
        raise EmulatorMemoryError("attempted to write to ROM!")

class RAM(MemoryDevice):
    def __init__(self, size: int):
        self.data = bytearray(size)
    def read(self, addr: int) -> int:
        return self.data[addr]
    def write(self, addr: int, value: int) -> None:
        self.data[addr] = value & 0xFF

class StdoutOutput(MemoryDevice):
    def write(self, addr: int, value: int) -> None:
        log.stdout(chr(value))
        # print(chr(value), end = "", flush = True)

class ResetBytes(MemoryDevice):
    def __init__(self, program_start_address: int = 0x0000):
        self.bytes = program_start_address

    def read(self, addr: int) -> int:
        match addr:
            case 0x0000:
                return (self.bytes >> 8) & 0xFF
            case 0x0001:
                return self.bytes & 0xFF
            case _:
                raise EmulatorMemoryError("outside of reset bytes")

class MU:
    def __init__(self, logger: Logger):
        self.log = logger
        global log
        log = self.log

        self.devices = []
        self.starts = []
        self.ends = []

        self.log.setup("created memory unit")

    def map_device(self, start: int, end: int, device: MemoryDevice) -> None:
        idx = bisect.bisect_right(self.starts, start)
        self.devices.insert(idx, device)
        self.starts.insert(idx, start)
        self.ends.insert(idx, end)

        self.log.setup(f"mapped device {type(device).__name__} to {hex(start)}-{hex(end)}")

    def get_device(self, addr: int) -> tuple:
        idx = bisect.bisect_right(self.starts, addr) - 1
        if idx >= 0 and addr <= self.ends[idx]:
            return self.devices[idx], self.starts[idx]

        raise EmulatorMemoryError(f"accessed unmapped memory address {hex(addr)}")

    def read(self, addr: int) -> int:
        device, base_addr = self.get_device(addr)
        try:
            value = device.read(addr - base_addr)
            self.log.memory(f"read {hex(value, 2)} from {hex(addr)}")
            return value
        except Exception as e:  # noqa: BLE001
            raise EmulatorMemoryError(f"error reading {hex(addr)}: {e}")

    def write(self, addr: int, value: int) -> None:
        device, base_addr = self.get_device(addr)
        try:
            self.log.memory(f"writing {hex(value, 2)} to {hex(addr)}")
            device.write(addr - base_addr, value)
        except Exception as e:  # noqa: BLE001
            raise EmulatorMemoryError(f"error writing to {hex(addr)}: {e}")
