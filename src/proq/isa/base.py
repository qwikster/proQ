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

    def operand(self, idx: int = 1) -> int: # 1-indexed
        return self.registers.PC + idx

    def pci(self, amt: int = 1): # 1-indexed
        self.registers.PC += amt

    def execute(self) -> Iterator[None]:
        yield

class DataMode(IntEnum):
    R_BYTE_W_REG = 0x00
    # BYTE WORD DWORD REGISTER IMMEDIATE
