from collections.abc import Iterator
from time import sleep

from proq.isa.base import Instruction


class NOP(Instruction):
    def execute(self) -> Iterator[None]:
        self.pci()
        yield

class HALT(Instruction):
    def execute(self) -> Iterator[None]:
        sleep(0.01) # cpu spinny
        yield # do not increment pc

class CPUID(Instruction): # yea idk what to do here
    def execute(self) -> Iterator[None]:
        self.registers[0] = 0x7072 # pr
        self.registers[1] = 0x6F51 # oQ
        self.registers[2] = 0x7630 # v0
        yield
        self.pci()
        yield
