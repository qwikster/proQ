from collections.abc import Iterator

from proq.isa.base import Instruction, RegisterOperand, SizeOperand
from proq.util.exceptions import InvalidModeByte


class NOP_ALIAS(Instruction):
    has_dst = has_src = False
    def execute(self) -> Iterator[None]:
        self.pci()
        yield

class JMP(Instruction):
    has_dst = False
    def execute(self) -> Iterator[None]:
        self.decode_mode_bytes()
        yield

        self.write_register(RegisterOperand.REG_PC, self.get_src_val())
        yield

class PUSH(Instruction): # pushes 2 bytes
    has_dst = False
    required_size = SizeOperand.WORD
    def execute(self) -> Iterator[None]:
        self.decode_mode_bytes()
        yield

        self.stack.push_len(self.get_src_val(), 2)
        yield

        self.pcio()
        yield

class POP(Instruction):
    has_src = False
    required_size = SizeOperand.WORD
    def execute(self) -> Iterator[None]:
        self.decode_mode_bytes()
        self.mode = self.mode._replace(size = SizeOperand.WORD) # must be one word
        yield

        self.write_dst(self.stack.pop_len(2))
        yield

        self.pcio()
        yield

class CALL(Instruction):
    has_dst = False
    required_size = SizeOperand.WORD
    def execute(self) -> Iterator[None]:
        self.decode_mode_bytes()
        yield

        dst = self.get_src_val()
        self.pcio()
        self.stack.push_len(self.registers.PC + 1, 2) # return to instruction after CALL
        self.registers.PC = dst
        yield

class RET(Instruction): # return
    has_src = has_dst = False
    def execute(self) -> Iterator[None]:
        self.registers.PC = self.stack.pop_len(2)
        yield
        yield

class PUSHF(Instruction):
    has_src = has_dst = False
    def execute(self) -> Iterator[None]:
        self.stack.push_flags()
        yield
        self.pci()
        yield

class POPF(Instruction):
    has_src = has_dst = False
    def execute(self) -> Iterator[None]:
        self.stack.pop_flags()
        yield
        self.pci()
        yield

# class TEST(Instruction):
#     def execute(self) -> Iterator[None]:
#         self.alu.do(Ops.ADD, 0, 1) # TODO
#         yield
