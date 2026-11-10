from collections.abc import Iterator

from proq.isa.base import Instruction, RegisterOperand, SizeOperand
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

class PUSH(Instruction): # pushes 2 bytes
    def execute(self) -> Iterator[None]:
        self.decode_mode_bytes()
        if self.mode.size.get_size != 2:
            raise InvalidModeByte("PUSH must be WORD")
        yield

        self.stack.push_len(self.get_src_val(), 2)
        yield

        self.pcio()
        yield

class POP(Instruction):
    def execute(self) -> Iterator[None]:
        self.decode_mode_bytes()
        self.mode = self.mode._replace(size = SizeOperand.BYTE) # must be one byte
        yield

        self.write_dst(self.stack.pop())
        yield

        self.pcio()
        yield

class CALL(Instruction):
    def execute(self) -> Iterator[None]:
        self.decode_mode_bytes()
        if self.mode.size.get_size() != 2:
            raise InvalidModeByte("CALL must be WORD")
        yield

        self.stack.push_len(self.registers.PC + 1, 2) # return to instruction after CALL
        self.registers.PC = self.get_src_val()
        yield

class RET(Instruction): # return
    def execute(self) -> Iterator[None]:
        self.registers.PC = self.stack.pop_len(2)
        yield
        yield

class PUSHF(Instruction):
    def execute(self) -> Iterator[None]:
        self.stack.push_flags()
        yield
        self.pci()
        yield

class POPF(Instruction):
    def execute(self) -> Iterator[None]:
        self.stack.pop_flags()
        yield
        self.pci()
        yield

# class TEST(Instruction):
#     def execute(self) -> Iterator[None]:
#         self.alu.do(Ops.ADD, 0, 1) # TODO
#         yield
