from collections.abc import Iterator

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
        self.registers.PC = # NEED RWORD AND WWORD
