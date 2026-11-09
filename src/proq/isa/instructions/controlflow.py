from collections.abc import Iterator

from proq.hw.alu import Ops
from proq.isa.base import Instruction, RegisterOperand, SizeOperand
from proq.isa.mixins import StackMixin
from proq.util.exceptions import InvalidModeByte


class NOP_ALIAS(Instruction):
    def execute(self) -> Iterator[None]:
        self.pci()
        yield

class JMP(Instruction):
    def execute(self) -> Iterator[None]:
        self.decode_mode_bytes()
        yield

        self.write_register(RegisterOperand.REG_PC, self.get_src_val())
        yield

class PUSH(Instruction, StackMixin):
    def execute(self) -> Iterator[None]:
        self.decode_mode_bytes()
        if self.mode.size.get_size != 2:
            raise InvalidModeByte("PUSH must be 1 byte")
        yield

        self.push(self.get_src_val())
        yield

        self.pcio()
        yield

class POP(Instruction, StackMixin):
    def execute(self) -> Iterator[None]:
        self.decode_mode_bytes()
        self.mode._replace(size = SizeOperand.BYTE) # must be one byte
        yield

        self.write_dst(self.pop())
        yield

        self.pcio()
        yield

class CALL(Instruction):
    def execute(self) -> Iterator[None]:
        yield

class RET(Instruction): # return
    def execute(self) -> Iterator[None]:
        yield

class PUSHF(Instruction, StackMixin):
    def execute(self) -> Iterator[None]:
        yield

# class TEST(Instruction):
#     def execute(self) -> Iterator[None]:
#         self.alu.do(Ops.ADD, 0, 1) # TODO
#         yield
