from typing import Protocol

from proq.isa.base import IsInstruction


class IsStackInstruction(IsInstruction, Protocol): #IsInstruction should only apply to subclasses of Instruction
    def push(self, value: int) -> None: ...
    def pop(self) -> int: ...

class StackMixin:
    def push(self: IsInstruction, value: int) -> None:
        addr = self.registers.SP
        self.mu.write(addr, value & 0xFF)
        self.registers.SP -= 1

    def pop(self: IsInstruction) -> int:
        value = self.mu.read(self.registers.SP)
        self.registers.SP += 1
        return value

    def push_flags(self: IsStackInstruction) -> None:
        self.push(self.registers.flags.export_int())

    def pop_flags(self: IsStackInstruction) -> None:
        self.registers.flags.import_int(self.pop())

    def push_len(self: IsStackInstruction, value: int, size: int) -> None:
        for i in range(size):
            self.push((value >> (8 * i)) & 0xFF)

    def pop_len(self: IsStackInstruction, size: int) -> int:
        value = 0
        for i in range(size - 1, -1, -1):
            value |= (self.pop() << (8 * i))
        return value
