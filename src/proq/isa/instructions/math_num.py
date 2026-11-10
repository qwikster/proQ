from collections.abc import Iterator

from proq.hw.alu import Ops
from proq.isa.base import Instruction


class INC(Instruction):
    def execute(self) -> Iterator[None]:
        self.decode_mode_bytes()
        yield

        value = self.read_dst()
        cf = self.registers.flags.CF
        value = self.alu.do(Ops.ADD, value, 1)
        yield

        self.write_dst(value)
        self.registers.flags.CF = cf # preserve x86 logic since ops.ADD changes it
        self.pcio()
        yield

class DEC(Instruction):
    def execute(self) -> Iterator[None]:
        self.decode_mode_bytes()
        yield

        value = self.read_dst()
        cf = self.registers.flags.CF
        value = self.alu.do(Ops.SUB, value, 1)
        yield

        self.write_dst(value)
        self.registers.flags.CF = cf # preserve x86 logic since ops.SUB changes it
        self.pcio()
        yield

class ADD(Instruction):
    def execute(self) -> Iterator[None]:
        self.decode_mode_bytes()
        yield

        a = self.read_dst()
        b = self.get_src_val()
        yield

        self.write_dst(self.alu.do(Ops.ADD, a, b))
        self.pcio()
        yield

class SUB(Instruction):
    def execute(self) -> Iterator[None]:
        self.decode_mode_bytes()
        yield

        a = self.read_dst()
        b = self.get_src_val()
        yield

        self.write_dst(self.alu.do(Ops.SUB, a, b))
        self.pcio()
        yield
