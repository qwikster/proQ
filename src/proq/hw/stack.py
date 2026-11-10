from proq.hw.mu import MU
from proq.hw.register import Registers
from proq.util.logging import Logger
from proq.util.util import hex


class Stack:
    def __init__(self, registers: Registers, mu: MU, logger: Logger):
        self.registers = registers
        self.mu = mu
        self.logger = logger

    def push(self, value: int) -> None:
        addr = self.registers.SP
        self.registers.SP -= 1
        self.registers.SP &= 0xFFFF
        self.mu.write(addr, value & 0xFF)
        self.logger.stack(f"pushed {hex(value)}")

    def pop(self) -> int:
        value = self.mu.read(self.registers.SP)
        self.registers.SP += 1
        self.registers.SP &= 0xFFFF
        self.logger.stack(f"popped {hex(value)}")
        return value

    def push_flags(self) -> None: # writes 2 bytes to keep it consistent
        self.push(0)
        self.push(self.registers.flags.export_int())

    def pop_flags(self) -> None:
        self.registers.flags.import_int(self.pop())
        self.pop()

    def push_len(self, value: int, size: int = 2) -> None:
        for i in range(size):
            self.push((value >> (8 * i)) & 0xFF)

    def pop_len(self, size: int = 2) -> int:
        value = 0
        for i in range(size - 1, -1, -1):
            value |= (self.pop() << (8 * i))
        return value
