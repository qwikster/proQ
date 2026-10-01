from proq.hw.alu import ALU
from proq.hw.cu import CU
from proq.hw.mu import MU, RAM, ROM, ResetBytes, StdoutOutput
from proq.hw.register import Registers
from proq.util.exceptions import EmulatorMemoryError
from proq.util.logging import Logger
from proq.util.util import MutableInt, hex

MAX_MEMORY = 61440

class CPU:
    def __init__(
        self,
        binary: bytes,
        logger: Logger,
        memsize: int = 4096,  # 4K
        romsize: int = 57344, # 56K
        flag_debug: bool = False,
        start_pos: int = 0x0000
    ):
        self.log = logger

        self.interrupt = MutableInt(0x00) # hardware interrupt line
        self.cycle = 0

        # Memory
        self.mu = MU(self.log)
        if memsize + romsize > MAX_MEMORY:
            raise EmulatorMemoryError(f"Assigning more RAM/ROM than is available (max: {hex(MAX_MEMORY)}, used: {hex(memsize + romsize)}")

        self.mu.map_device(0x0000, romsize - 1, ROM(size = romsize, binary = binary))
        self.mu.map_device(romsize, romsize + memsize - 1, RAM(size = memsize))
        self.mu.map_device(0xF000, 0xF000, StdoutOutput())
        self.mu.map_device(0xFFFE, 0xFFFF, ResetBytes(start_pos))

        # Registers
        self.registers = Registers(self.log, stack_addr = romsize + memsize - 1, debug = flag_debug)

        # Instructions
        self.alu = ALU()
        self.cu = CU(self.alu, self.mu, self.registers, logger = logger)

    def tick(self):
        self.cycle += 1
        self.cu.tick(self.interrupt)
