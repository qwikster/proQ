from dataclasses import dataclass, field

from proq.util.logging import Logger
from proq.util.util import hex


@dataclass
class Flags:
    ZF: bool = False # Zero flag
    CF: bool = False # Carry
    SF: bool = False # Sign
    OF: bool = False # Overflow
    IF: bool = False # enable interrupts
    TF: bool = False # Trap: step one at a time

    def export_int(self):
        value = 0b000000
        flags = [self.ZF, self.CF, self.SF, self.OF, self.IF, self.TF]
        for i, flag in enumerate(flags):
            if flag:
                value |= (1 << i)
        return value

    def import_int(self, value: int):
        (self.ZF, self.CF, self.SF, self.OF, self.IF, self.TF) = (
            bool((value >> i) & 1) for i in range(6)
        )

@dataclass
class Registers:
    log: Logger

    stack_addr: int
    debug: bool = False

    PC: int = 0x0000 # program counter
    IR: int = 0x00   # instruction register
    SP: int = 0x0000 # stack pointer
    flags: Flags = field(default_factory=Flags)
    GPR: list[int] = field(default_factory=lambda: [0x0000] * 12) # general purpose registers

    def __post_init__(self):
        self.SP = self.stack_addr
        self.flags.TF = self.debug
        self.log.setup(f"Set up registers: PC {hex(self.PC)} | SP {hex(self.SP)} | IR {hex(self.IR)}")
        self.log.setup(f"GPR 1 thru 12: {self.GPR}")
        self.log.setup(f"{self.flags}")

    # cpu.registers[3] = 0x1234
    def __getitem__(self, idx: int) -> int:
        self.log.register(f"Read {hex(self.GPR[idx])} from R{idx}")
        return self.GPR[idx]

    def __setitem__(self, idx: int, value: int):
        self.GPR[idx] = value & 0xFFFF
        self.log.register(f"Wrote {hex(value)} to R{idx}")
