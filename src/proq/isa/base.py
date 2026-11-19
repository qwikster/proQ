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

_REGISTER_TYPE = (TypeOperand.REGISTER, TypeOperand.MEMORY_ID)
_NOT_POINTER = (RegisterOperand.REG_FLAG, RegisterOperand.REG_IR)

class Instruction:
    registry: ClassVar[dict[int, type]] = {}
    skipped: ClassVar[list[str]] = []

    # subclass overrides
    has_dst: ClassVar[bool] = True
    has_src: ClassVar[bool] = True
    required_size: ClassVar[SizeOperand | None] = None # ex. WORD for JMP/CALL/PUSH
    allow_dword: ClassVar[bool] = False # ex. for MUL
    uses_special: ClassVar[bool] = False

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

        self.pc_offset = 1 # consumed bytes
        self.lock_pc = False
        self.size = 2 # bytes used by memroy/immediate
        self.dst_offset = 0
        self.src_offset = 0

    def operand(self, idx: int = 1) -> int: # 1-indexed, *gets address*
        return self.registers.PC + idx

    def read_op(self, idx: int = 1, size: int = 1) -> int:
        value = 0
        for i in range(size):
            value = (value << 8) | self.mu.read(self.operand(idx + i))
        return value

    def fetch(self, size: int = 1) -> int:
        value = self.read_op(self.pc_offset, size)
        self.pc_offset += size
        return value

    def pci(self, amt: int = 1): # 1-indexed
        self.registers.PC = (self.registers.PC + amt) & 0xFFFF

    def pcio(self) -> None: # use on finish: move pc to end
        if not self.lock_pc:
            self.pci(self.pc_offset)

    @property
    def next_pc(self) -> int:
        return (self.registers.PC + self.pc_offset) & 0xFFFF

    def decode_mode_bytes(self, offset: int = 1) -> None:
        byte = self.read_op(offset)

        dst = TypeOperand((byte >> 6) & 0b11)
        src = TypeOperand((byte >> 4) & 0b11)
        size = SizeOperand((byte >> 2) & 0b11)
        special = byte & 0b11
        name = type(self).__name__

        if special and not self.uses_special:
            raise InvalidModeByte(f"{name}: special bits must be 0")
        if not self.has_dst and dst != TypeOperand.IMMEDIATE_OR_NULL:
            raise InvalidModeByte(f"{name} takes no DST value")
        if not self.has_src and dst != TypeOperand.IMMEDIATE_OR_NULL:
            raise InvalidModeByte(f"{name}: takes no SRC value")
        if self.has_dst and dst == TypeOperand.IMMEDIATE_OR_NULL:
            raise InvalidModeByte(f"{name}: destination can't be immediate")

        has_registers = (self.has_dst and dst in _REGISTER_TYPE) or (self.has_src and src in _REGISTER_TYPE)
        reg_dst, reg_src = (RegisterOperand(0), RegisterOperand(0)) # shouldnt actually be 0, unreachable default
        if has_registers:
            reg_byte = self.read_op(offset + 1)
            reg_dst = RegisterOperand(reg_byte >> 4) # left
            reg_src = RegisterOperand(reg_byte & 0b1111) # right

        if self.has_dst and dst == TypeOperand.MEMORY_ID and reg_dst in _NOT_POINTER:
            raise InvalidModeByte(f"{name}: {reg_dst.name} doesn't fit memory addresses")
        if self.has_src and src == TypeOperand.MEMORY_ID and reg_src in _NOT_POINTER:
            raise InvalidModeByte(f"{name}: {reg_src.name} doesn't fit memory addresses")

        sized = (self.has_dst and dst in (TypeOperand.MEMORY_DR, TypeOperand.MEMORY_ID)) or (
            self.has_src and src != TypeOperand.REGISTER
        ) # don't need size for register stuff (16 bit)
        if self.required_size is not None and size != self.required_size:
            raise InvalidModeByte(f"{name} requires size {self.required_size.name}")
        if sized:
            if size == SizeOperand.ZERO or (size == SizeOperand.DWORD and not self.allow_dword):
                raise InvalidModeByte(f"{name}: size {size.name} invalid in this case")
            self.size = size.get_size()
        else:
            if size not in (SizeOperand.ZERO, SizeOperand.WORD):
                raise InvalidModeByte(f"{name}: register only operations require WORD")
            self.size = 2

        header = offset + 1 + (1 if has_registers else 0)
        dst_len = 2 if self.has_dst and dst == TypeOperand.MEMORY_DR else 0
        src_len = 0
        if self.has_src:
            if src == TypeOperand.IMMEDIATE_OR_NULL:
                src_len = self.size
            elif src == TypeOperand.MEMORY_DR:
                src_len = 2

        self.dst_offset = header
        self.src_offset = header + dst_len
        self.pc_offset = header + dst_len + src_len # total!

        self.mode = ModeBytes(dst, src, size, special, has_registers, reg_dst, reg_src)
        self.logger.modes(f"{self.mode}, length: {self.pc_offset}")

    def pointer(self, id: RegisterOperand) -> int:
        if id in _NOT_POINTER:
            raise InvalidModeByte(f"{id.name} cannot be a memory pointer")
        return self.read_register(id)

    def read_register(self, id: RegisterOperand) -> int:
        match id:
            case RegisterOperand.REG_FLAG:
                return self.registers.flags.export_int()
            case RegisterOperand.REG_PC:
                return self.next_pc
            case RegisterOperand.REG_IR:
                return self.registers.IR
            case RegisterOperand.REG_SP:
                return self.registers.SP
            case _:
                return self.registers.GPR[id]

    def write_register(self, id: RegisterOperand, value: int) -> None:
        value &= 0xFFFF
        match id:
            case RegisterOperand.REG_FLAG:
                self.registers.flags.import_int(value)
            case RegisterOperand.REG_IR:
                raise InvalidModeByte("No point in writing to IR")
            case RegisterOperand.REG_PC:
                self.lock_pc = True
                self.registers.PC = value
            case RegisterOperand.REG_SP:
                self.registers.SP = value
            case _:
                self.registers.GPR[id] = value

    def get_src_val(self) -> int:
        if not self.has_src:
            raise RuntimeError(f"{type(self).__name__} claims no source operand")

        match self.mode.src:
            case TypeOperand.IMMEDIATE_OR_NULL:
                return self.read_op(self.src_offset, self.size)
            case TypeOperand.REGISTER:
                return self.read_register(self.mode.reg_src)
            case TypeOperand.MEMORY_DR:
                return self.mu.read_len(self.read_op(self.src_offset, 2), self.size)
            case TypeOperand.MEMORY_ID:
                return self.mu.read_len(self.pointer(self.mode.reg_src), self.size)

    def read_dst(self) -> int:
        if not self.has_dst:
            raise RuntimeError(f"{type(self).__name__} claims no destination operand")

        match self.mode.dst:
            case TypeOperand.REGISTER:
                return self.read_register(self.mode.reg_dst)
            case TypeOperand.MEMORY_DR:
                return self.mu.read_len(self.read_op(self.dst_offset, 2), self.size)
            case TypeOperand.MEMORY_ID:
                return self.mu.read_len(self.pointer(self.mode.reg_dst), self.size)
            case _:
                raise InvalidModeByte("Destination cannot be Immediate! or you did something Really wrong")

    def write_dst(self, value: int) -> None:
        value &= (1 << (8 * self.size)) - 1 # BYTE should write low byte
        if not self.has_dst:
            raise RuntimeError(f"{type(self).__name__} claims no destination operand")

        match self.mode.dst:
            case TypeOperand.REGISTER:
                self.write_register(self.mode.reg_dst, value)
                self.logger.modes(f"wrote {value:#06X} to {self.mode.reg_dst.name}")

            case TypeOperand.MEMORY_DR:
                addr = self.read_op(self.dst_offset, 2)
                self.mu.write_len(addr, value, self.size)
                self.logger.modes(f"wrote {value:#X} ({self.size} bytes) to {addr:#06X}")

            case TypeOperand.MEMORY_ID:
                addr = self.pointer(self.mode.reg_dst)
                self.mu.write_len(addr, value, self.size)
                self.logger.modes(f"wrote {value:#X} to [{self.mode.reg_dst.name}] = {addr:#06X}")

            case _:
                raise InvalidModeByte("Destination cannot be Immediate! or you did something Really wrong")

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
