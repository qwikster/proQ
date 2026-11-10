from __future__ import annotations

from collections.abc import Iterator
from enum import IntEnum
from typing import TYPE_CHECKING, ClassVar, NamedTuple, Protocol

from proq.hw.stack import Stack
from proq.isa.set import Op
from proq.util.exceptions import InvalidModeByte
from proq.util.logging import Logger

if TYPE_CHECKING:
    from proq.hw.alu import ALU
    from proq.hw.mu import MU
    from proq.hw.register import Registers

class TypeOperand(IntEnum):
    IMMEDIATE_OR_NULL = 0
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

    def __init__(self, mu: MU, alu: ALU, registers: Registers, stack: Stack, logger: Logger):
        self.alu = alu
        self.mu = mu
        self.stack = stack
        self.registers = registers
        self.logger = logger

        self.pc_offset = 0
        self.lock_pc = False

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

    def pcio(self) -> None: # use on finish: move pc to end
        if not self.lock_pc:
            self.pci(self.pc_offset)

    def decode_mode_bytes(self, offset: int = 1) -> None:
        byte = self.read_op(offset)

        dst = TypeOperand((byte >> 6) & 0b11)
        src = TypeOperand((byte >> 4) & 0b11)
        size = SizeOperand((byte >> 2) & 0b11)
        special = byte & 0b11

        if has_registers := dst in (1, 3) or src in (1, 3):
            reg_byte = self.read_op(offset + 1)
            reg_dst = RegisterOperand((reg_byte >> 4) & 0b1111) # left
            reg_src = RegisterOperand(reg_byte & 0b1111) # right
            self.pc_offset += 3 # opcode + mode byte(s)
        else:
            # shouldnt actually be 0, unreachable default
            self.pc_offset += 4
            reg_dst, reg_src = (RegisterOperand(0), RegisterOperand(0))

        self.mode = ModeBytes(dst, src, size, special, has_registers, reg_dst, reg_src)
        self.logger.modes(str(self.mode))

    def read_register(self, id: RegisterOperand, indirect: bool = False) -> int:
        if indirect and id in (RegisterOperand.REG_FLAG, RegisterOperand.REG_IR):
            raise InvalidModeByte("Tried to read indirect from special register")
        match id:
            case RegisterOperand.REG_FLAG:
                return self.registers.flags.export_int()
            case RegisterOperand.REG_PC:
                return self.registers.PC
            case RegisterOperand.REG_IR:
                return self.registers.IR
            case RegisterOperand.REG_SP:
                return self.registers.SP
            case _:
                return self.registers.GPR[id]

    def write_register(self, id: RegisterOperand, value: int, indirect: bool = False) -> None:
        if indirect and id in (RegisterOperand.REG_FLAG, RegisterOperand.REG_IR):
            raise InvalidModeByte("Tried to write indirect to special register")
        match id:
            case RegisterOperand.REG_FLAG:
                self.registers.flags.import_int(value)
            case RegisterOperand.REG_IR:
                raise InvalidModeByte("No point in writing to IR")
            case RegisterOperand.REG_PC:
                if indirect:
                    self.mu.write_len(self.registers.PC, self.mode.size.get_size(), value)
                else:
                    self.lock_pc = True
                    self.registers.PC = value & 0xFFFF
            case RegisterOperand.REG_SP:
                if indirect:
                    self.mu.write_len(self.registers.SP, self.mode.size.get_size(), value)
                else:
                    self.registers.SP = value & 0xFFFF
            case _:
                self.registers.GPR[id] = value

    def get_src_val(self) -> int:
        self.pc_offset += 2 if self.mode.dst == TypeOperand.MEMORY_DR else 0 # size that memory address could take

        match self.mode.src:
            case TypeOperand.IMMEDIATE_OR_NULL:
                value = self.read_op(self.pc_offset, self.mode.size.get_size())
                self.pc_offset += self.mode.size.get_size()
                return value

            case TypeOperand.REGISTER:
                return self.read_register(self.mode.reg_src)

            case TypeOperand.MEMORY_DR:
                addr = self.mu.read_len(self.read_op(self.pc_offset), 2)
                self.pc_offset += 2
                return self.mu.read_len(addr, self.mode.size.get_size())

            case TypeOperand.MEMORY_ID:
                addr = self.read_register(self.mode.reg_src, indirect = True)
                return self.mu.read_len(addr, self.mode.size.get_size())

    def write_dst(self, value: int) -> None:
        match self.mode.dst:
            case TypeOperand.IMMEDIATE_OR_NULL: # shouldn't happen!
                raise RuntimeError("Tried to check destination on an operation that only takes a source value")

            case TypeOperand.REGISTER:
                if self.mode.size.get_size == SizeOperand.DWORD:
                    raise InvalidModeByte("Can't write a dword to a register")
                self.write_register(self.mode.reg_dst, value)
                self.logger.modes(f"wrote {value} to {self.mode.reg_dst}")

            case TypeOperand.MEMORY_DR:
                offset = 3 if self.mode.has_registers else 2
                self.mu.write_len(self.read_op(offset, 2), value, self.mode.size.get_size())
                self.logger.modes(f"wrote {value} of {self.mode.size.get_size()} to {self.read_op(offset, 2)}")

            case TypeOperand.MEMORY_ID:
                self.write_register(self.mode.reg_dst, value, indirect = True)
                self.logger.modes(f"wrote {value} to reg {self.mode.reg_dst}")

    def read_dst(self) -> int:
        match self.mode.dst:
            case TypeOperand.IMMEDIATE_OR_NULL: # shouldn't happen!
                raise RuntimeError("Destination cannot be Immediate")

            case TypeOperand.REGISTER:
                return self.read_register(self.mode.reg_dst)

            case TypeOperand.MEMORY_DR:
                offset = 3 if self.mode.has_registers else 2
                return self.mu.read_len(self.read_op(offset, 2), self.mode.size.get_size())

            case TypeOperand.MEMORY_ID:
                return self.read_register(self.mode.reg_dst, indirect = True)

    def execute(self) -> Iterator[None]:
        yield

class IsInstruction(Protocol):
    alu: ALU
    mu: MU
    registers: Registers
    logger: Logger
    def decode_mode_bytes(self) -> None:...
    def read_dst(self) -> int:...
    def get_src_val(self) -> int:...
    def write_dst(self, value: int) -> None:...
    def pcio(self) -> None:...
    # def a(self) -> a:...
