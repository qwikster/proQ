from collections.abc import Iterator

from proq.isa.base import Instruction


class ADD(Instruction):
    def execute(self) -> Iterator[None]:
        yield

class SUB(Instruction):
    def execute(self):
        self.registers.PC += 0x01
        yield
