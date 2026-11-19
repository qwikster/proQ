import random
from collections.abc import Iterator

from proq.isa.base import Instruction, SizeOperand


class NOP(Instruction):
    def execute(self) -> Iterator[None]:
        self.pci()
        yield

class BREAK(Instruction):
    def execute(self) -> Iterator[None]:
        input("waiting... [press enter]")
        self.pci()
        yield

class HALT(Instruction):
    def execute(self) -> Iterator[None]:
        self.pci()
        self.mu.halted = True
        self.mu.log.cu("HALTed, CTRL+C to quit")
        yield

class CPUID(Instruction): # yea idk what to do here
    def execute(self) -> Iterator[None]:
        self.registers[0] = 0x7072 # pr
        self.registers[1] = 0x6F51 # oQ
        self.registers[2] = 0x7630 # v0
        yield
        self.pci()
        yield

class RAND(Instruction): # get random byte
    required_size = SizeOperand.BYTE
    def execute(self) -> Iterator[None]:
        self.decode_mode_bytes()
        yield

        limit = (val := self.get_src_val()) or 0xFF
        result = random.randint(0, limit)
        yield

        self.write_dst(result)
        self.pcio()
        yield
