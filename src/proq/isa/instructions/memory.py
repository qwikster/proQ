from collections.abc import Iterator

from proq.isa.base import Instruction, RegisterOperand, SizeOperand, TypeOperand


class MOV(Instruction):
    def execute(self) -> Iterator[None]:
        mode = self.decode_mode_bytes(1)
        self.pci(2 if mode.has_registers else 1)
        yield

        value = 0
        match mode.src:
            case TypeOperand.IMMEDIATE:
                value = self.read_op(1, size = mode.reg_src)
                self.pci(mode.reg_src)
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

        yield
        match dst:
            case TypeOperand.MEMORY_DR:
                self.mu.write(self.read_op(1, size = 2), value)

# (high_byte << 8) | low_byte
