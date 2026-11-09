from proq.hw.mu import MU
from proq.hw.register import Registers


class Stack:
    def __init__(self, registers: Registers, mu: MU):
        self.registers = registers
        self.mu = mu

    def push(self, value: int) -> None:
        addr = self.registers.SP
        self.mu.write(addr, value & 0xFF)
        self.registers.SP -= 1

    def pop(self) -> int:
        value = self.mu.read(self.registers.SP)
        self.registers.SP += 1
        return value

    def push_flags(self) -> None:
        self.push(self.registers.flags.export_int())

    def pop_flags(self) -> None:
        self.registers.flags.import_int(self.pop())

    def push_len(self, value: int, size: int) -> None:
        for i in range(size):
            self.push((value >> (8 * i)) & 0xFF)

    def pop_len(self, size: int) -> int:
        value = 0
        for i in range(size - 1, -1, -1):
            value |= (self.pop() << (8 * i))
        return value
