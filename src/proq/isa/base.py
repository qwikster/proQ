from __future__ import annotations

from collections.abc import Iterator
from typing import TYPE_CHECKING, ClassVar

from proq.isa.set import Op

if TYPE_CHECKING:
    from proq.hw.alu import ALU
    from proq.hw.mu import MU
    from proq.hw.register import Registers

class Instruction:
    registry: ClassVar[dict[int, type]] = {}
    skipped: ClassVar[list[str]] = []

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        try:
            op = Op[cls.__name__]
            cls.opcode = op.value
            Instruction.registry[op.value] = cls
        except KeyError:
            Instruction.skipped.append(cls.__name__)

    def __init__(self, mu: MU, alu: ALU, registers: Registers):
        self.alu = alu
        self.mu = mu
        self.registers = registers

    def operand(self, idx: int = 1) -> int: # 1-indexed, *gets address*
        return self.registers.PC + idx

    def read_op(self, idx: int = 1, size: int = 1) -> int:
        value = 0
        for i in range(size):
            value = (value << 8) | self.mu.read(self.operand(idx + i))
        return value


    def pci(self, amt: int = 1): # 1-indexed
        self.registers.PC += amt
        self.registers.PC &= 0xFFFF

    def execute(self) -> Iterator[None]:
        yield
