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
        if self.iterable:
            try:
                next(self.iterable)
                self.logger.clock("Next cycle")
                return
            except StopIteration:
                pass

        if interrupt.value != 0:
            self.logger.interrupt(f"loading interrupt {hex(int(interrupt), 2)}")
            input()
            return

            instance = instruction(self.mu, self.alu, self.registers)
            self.logger.cu(f"Running instruction {hex(opcode, 2)} ({instruction.__name__})")
            self.iterable = instance.execute()

        try:
            next(self.iterable)
            self.logger.clock("Next cycle")
        except StopIteration:
            self.iterable = None
