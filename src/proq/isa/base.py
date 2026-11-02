from __future__ import annotations

from collections.abc import Iterator
from enum import IntEnum
from typing import TYPE_CHECKING, ClassVar, NamedTuple

from proq.isa.set import Op

if TYPE_CHECKING:
    from proq.hw.alu import ALU
    from proq.hw.mu import MU
    from proq.hw.register import Registers

class TypeOperand(IntEnum):
    IMMEDIATE = 0
    REGISTER  = 1
    MEMORY_DR = 2 # direct [Addr]
    MEMORY_ID = 3 # indirect [Reg]

class SizeOperand(IntEnum):
    ZERO = 0
    BYTE = 1
    WORD = 2
    DWORD = 3

    def get_size(self):
        return self.value if self.value <= 2 else 4 # dword

class RegisterOperand(IntEnum):
    REG_0 = 0
    REG_1 = 1
    REG_2 = 2
    REG_3 = 3
    REG_4 = 4
    REG_5 = 5
    REG_6 = 6
    REG_7 = 7
    REG_8 = 8
    REG_9 = 9
    REG_10 = 10
    REG_11 = 11
    REG_PC = 12
    REG_IR = 13
    REG_SP = 14
    REG_FLAG = 15

class ModeBytes(NamedTuple):
    dst: TypeOperand
    src: TypeOperand
    size: SizeOperand
    special: int # also 2 bits
    has_registers: bool
    reg_dst: RegisterOperand
    reg_src: RegisterOperand

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

    def decode_mode_bytes(self, offset: int = 1) -> ModeBytes:
        byte = self.read_op(offset)

        dst = TypeOperand((byte >> 6) & 0b11)
        src = TypeOperand((byte >> 4) & 0b11)
        size = SizeOperand((byte >> 2) & 0b11)
        special = byte & 0b11

        if has_registers := dst in (1, 3) or src in (1, 3):
            reg_byte = self.read_op(offset + 1)
            reg_dst = RegisterOperand((reg_byte >> 4) & 0b1111) # left
            reg_src = RegisterOperand(reg_byte & 0b1111) # right
        else:
            # shouldnt actually be 0, unreachable default
            reg_dst, reg_src = (RegisterOperand(0), RegisterOperand(0))

        return ModeBytes(dst, src, size, special, has_registers, reg_dst, reg_src)

    def execute(self) -> Iterator[None]:
        yield
