from collections.abc import Iterator

from proq.hw.alu import Ops
from proq.isa.base import Instruction


class NOP_ALIAS(Instruction):
    def execute(self) -> Iterator[None]:
        self.pci()
        yield

class JMP(Instruction):
    def execute(self) -> Iterator[None]:
        loc_l = self.operand(1)
        loc_h = self.operand(2)
        yield

class TEST(Instruction):
    def execute(self) -> Iterator[None]:
        self.alu.do(Ops.ADD, 0, 1) # TODO
        yield
