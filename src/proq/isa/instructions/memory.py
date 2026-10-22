from collections.abc import Iterator

from proq.isa.base import Instruction
from proq.util.util import decode_mode_bytes, TypeOperand, RegisterOperand

class MOV(Instruction):
    def execute(self) -> Iterator[None]:
        dst_reg = 0
        src_reg = 0

        dst, src, reg = decode_mode_bytes(self.read_op(1), False)
        if reg:
            dst_reg, src_reg, reg = decode_mode_bytes(self.read_op(2), True)

        self.pci(2 if reg else 1)
        yield

        value = 0
        match src:
            case TypeOperand.IMMEDIATE:
                value = self.read_op(1)
                self.pci()
            case TypeOperand.REGISTER:
                match src_reg:
                    case RegisterOperand.REG_FLAG:
                        value = self.registers.flags.export_int()
                    case RegisterOperand.REG_PC:
                        value = self.registers.PC
                    case RegisterOperand.REG_SP:
                        value = self.registers.SP
                    case RegisterOperand.REG_IR:
                        value = self.registers.IR
                    case _:
                        value = self.registers.GPR[src_reg]
            case TypeOperand.MEMORY_DR:
                value = self.read_op()

        # NOTE: no idea if the read_op addresses line up, fix that, MEMORY_IR may need to be put in the same category as `case TypeOperand.REGISTER:`.
