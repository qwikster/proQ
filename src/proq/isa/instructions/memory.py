from collections.abc import Iterator

from proq.isa.base import Instruction
from proq.util.util import RegisterOperand, TypeOperand, decode_mode_bytes


class MOV(Instruction):
    def execute(self) -> Iterator[None]:
        dst_reg = 0
        src_reg = 0

        dst, src, reg = decode_mode_bytes(self.read_op(1), False)
        if reg:
            dst_reg, src_reg, reg = decode_mode_bytes(self.read_op(2), True)

        self.pci(2 if reg else 1)
        yield

        length, value = (0, 0)
        match src:
            case TypeOperand.IMMEDIATE:
                length = src_reg
                value = self.read_op(1, size = src_reg)
                self.pci(src_reg)
            case TypeOperand.MEMORY_DR:
                value = self.mu.read(self.read_op(1, size = 2))
                self.pci(2)
            case TypeOperand.REGISTER | TypeOperand.MEMORY_ID:
                match src_reg:
                    case RegisterOperand.REG_FLAG:
                        value = self.registers.flags.export_int()
                    case RegisterOperand.REG_PC:
                        value = self.registers.PC
                    case RegisterOperand.REG_SP:
                        value = self.registers.SP
                    case RegisterOperand.REG_IR:
                        value = self.registers.IR
                    case _: # MEMORY_ID must be this value
                        if src == TypeOperand.REGISTER:
                            value = self.registers.GPR[src_reg]
                        else:
                            value = self.mu.read(self.registers.GPR[src_reg])

        match dst:
            case TypeOperand.MEMORY_DR:
                self.mu.write(self.read_op(1, size = 2), value)

# (high_byte << 8) | low_byte
