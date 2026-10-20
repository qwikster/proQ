import proq.isa.instructions  # noqa: F401 # Have to add this to force it to run proq.isa.instructions.__init__.py n do the stuff
from proq.hw.alu import ALU
from proq.hw.mu import MU
from proq.hw.register import Registers
from proq.isa.base import Instruction
from proq.isa.set import Op
from proq.util.exceptions import InstructionNotImplementedError
from proq.util.logging import Logger
from proq.util.util import MutableInt, hex


class CU:
    def __init__(self, alu: ALU, mu: MU, registers: Registers, logger: Logger):
        for skipped in Instruction.skipped:
            logger.setup(f"Skipped unregistered instruction: {skipped}")

        for op in Op:
            if op.value not in Instruction.registry:
                raise InstructionNotImplementedError(f"No matching Class(Instruction) definition for {op.name} ({hex(op.value)})")

        self.alu = alu
        self.mu = mu
        self.registers = registers

        self.logger = logger

        self.iterable = None

    def tick(self, interrupt: MutableInt):
        self.logger.clock("Next cycle")

        if self.iterable:
            try:
                next(self.iterable)
                return
            except StopIteration:
                pass

        if interrupt.value != 0:
            interrupt.value = 0 # reset
            if not self.registers.flags.IF:
                pass
            self.logger.interrupt(f"loading interrupt {hex(int(interrupt), 2)}")
            self.registers.PC = self.mu.read(0xF100 + interrupt.value)
            self.registers.flags.IF = False
            self.registers.flags.TF = False

            # push flags and PC
            self.registers.SP -= 1
            self.mu.write(self.registers.SP, self.registers.flags.export_int())
            self.registers.SP -= 1
            self.mu.write(self.registers.SP, (self.registers.PC >> 8) & 0xFF) # high
            self.registers.SP -= 1
            self.mu.write(self.registers.SP, self.registers.PC & 0xFF) # low

        opcode = self.mu.read(self.registers.PC)
        self.registers.IR = opcode
        instruction = Instruction.registry.get(opcode)

        if not instruction:
            self.logger.cu(f"Invalid instruction {hex(opcode, 2)}")
            interrupt.set(0x01) # invalid opcode
            return

        instance = instruction(self.mu, self.alu, self.registers)
        self.logger.cu(f"Running instruction {hex(opcode, 2)} ({instruction.__name__})")
        self.iterable = instance.execute()

        try:
            next(self.iterable)
        except StopIteration:
            self.iterable = None
