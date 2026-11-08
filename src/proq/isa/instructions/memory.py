from collections.abc import Iterator

from proq.isa.base import Instruction, RegisterOperand, SizeOperand, TypeOperand
from proq.util.exceptions import InvalidModeByte


class MOV(Instruction):
    def execute(self) -> Iterator[None]:
        mode = self.decode_mode_bytes(1)
        self.pci(2 if mode.has_registers else 1)
        yield

        value = 0
        match mode.src:
            case TypeOperand.IMMEDIATE:
                value = self.read_op(1, size = mode.size.get_size())
                self.pci(mode.size.get_size())
            case TypeOperand.MEMORY_DR:
                value = self.mu.read(self.read_op(1, size = 2))
                self.pci(2)

            case TypeOperand.REGISTER | TypeOperand.MEMORY_ID:
                match mode.reg_src:
                    case RegisterOperand.REG_FLAG:
                        if mode.src == TypeOperand.MEMORY_ID:
                            raise InvalidModeByte("Tried to read indirect from special register")
                        value = self.registers.flags.export_int()
                    case RegisterOperand.REG_PC:
                        if mode.src == TypeOperand.MEMORY_ID:
                            raise InvalidModeByte("Tried to read indirect from special register")
                        value = self.registers.PC
                    case RegisterOperand.REG_SP:
                        if mode.src == TypeOperand.MEMORY_ID:
                            raise InvalidModeByte("Tried to read indirect from special register")
                        value = self.mu.read(self.registers.SP) if mode.src == TypeOperand.MEMORY_ID else self.registers.SP
                    case RegisterOperand.REG_IR:
                        if mode.src == TypeOperand.MEMORY_ID:
                            raise InvalidModeByte("Tried to read indirect from special register")
                        value = self.registers.IR
                    case _: # MEMORY_ID must be this value
                        if mode.src == TypeOperand.REGISTER:
                            value = self.registers.GPR[mode.reg_src]
                        else:
                            value = self.mu.read(self.registers.GPR[mode.reg_src])

        yield
        match mode.dst:
            case TypeOperand.MEMORY_DR:
                self.mu.write(self.read_op(1, size = mode.size.get_size()), value)
                self.pci(2)
            case TypeOperand.REGISTER | TypeOperand.MEMORY_ID:
                match mode.reg_dst:
                    case RegisterOperand.REG_FLAG:
                        if mode.dst == TypeOperand.MEMORY_ID:
                            raise InvalidModeByte("Tried to write indirect from special register")
                        self.registers.flags.import_int(value)
                    case RegisterOperand.REG_PC:
                        self.registers.PC = value
                    case RegisterOperand.REG_SP:
                        if mode.dst == TypeOperand.MEMORY_ID:
                            self.registers.SP = value
                        else:
                            self.mu.write(self.registers.SP, value)

                    case RegisterOperand.REG_IR:
                        if mode.dst == TypeOperand.MEMORY_ID:
                            raise InvalidModeByte("Tried to write indirect from special register")
                        self.registers.IR = value
                    case _:
                        if mode.src == TypeOperand.REGISTER:
                            self.registers.GPR[mode.reg_src] = value
                        else:
                            self.mu.write_len(self.registers.GPR[mode.reg_src], value, mode.size.get_size())

        self.pci(1)
        yield
