from collections.abc import Iterator
from typing import Protocol

from proq.hw.alu import Ops
from proq.isa.base import Instruction, IsInstruction


class IsStackInstruction(IsInstruction, Protocol): #IsInstruction should only apply to subclasses of Instruction
    def push(self, value: int) -> None: ...
    def pop(self) -> int: ...

class BasicMathInstruction(Instruction):
    op = Ops.NEG # change this!!!!!!
    def execute(self) -> Iterator[None]:
        self.decode_mode_bytes()
        yield

        a = self.read_dst()
        b = self.get_src_val()
        yield

        self.write_dst(self.alu.do(self.op, a, b))
        self.pcio()
        yield
