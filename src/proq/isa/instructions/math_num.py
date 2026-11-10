from collections.abc import Iterator

from proq.hw.alu import Ops
from proq.isa.base import Instruction, TypeOperand
from proq.util.exceptions import InvalidModeByte


class INC(Instruction):
    def execute(self) -> Iterator[None]:
        self.decode_mode_bytes()
        yield

        match self.mode.src:
            case TypeOperand.IMMEDIATE_OR_NULL:
                raise InvalidModeByte("Cannot increment immediate value")
            case TypeOperand.REGISTER:
                a = self.read_register(self.mode.reg_src)
                self.write_register(self.mode.reg_src, (a + 1) & 0xFFFF)
            case TypeOperand.MEMORY_DR:
                addr = self.mu.read_len(self.read_op(self.pc_offset), 2)
                self.pc_offset += 2
                a = self.mu.read_len(addr, self.mode.size.get_size())
                self.mu.write_len(addr, (a + 1) & 0xFFFF, self.mode.size.get_size())
            case TypeOperand.MEMORY_ID:
                addr = self.read_register(self.mode.reg_src, indirect = True)
                a = self.mu.read_len(addr, self.mode.size.get_size())
                self.mu.write_len(addr, (a + 1) & 0xFFFF, self.mode.size.get_size())
        yield

        self.pcio()
        yield

class DEC(Instruction):
    def execute(self) -> Iterator[None]:
        self.decode_mode_bytes()
        yield

        match self.mode.src:
            case TypeOperand.IMMEDIATE_OR_NULL:
                raise InvalidModeByte("Cannot decrement immediate value")
            case TypeOperand.REGISTER:
                a = self.read_register(self.mode.reg_src)
                self.write_register(self.mode.reg_src, (a - 1) & 0xFFFF)
            case TypeOperand.MEMORY_DR:
                addr = self.mu.read_len(self.read_op(self.pc_offset), 2)
                self.pc_offset += 2
                a = self.mu.read_len(addr, self.mode.size.get_size())
                self.mu.write_len(addr, (a - 1) & 0xFFFF, self.mode.size.get_size())
            case TypeOperand.MEMORY_ID:
                addr = self.read_register(self.mode.reg_src, indirect = True)
                a = self.mu.read_len(addr, self.mode.size.get_size())
                self.mu.write_len(addr, (a - 1) & 0xFFFF, self.mode.size.get_size())
        yield

        self.pcio()
        yield


class ADD(Instruction):
    def execute(self) -> Iterator[None]:
        self.decode_mode_bytes()
        yield

        a = self.get_src_val()

        b = self.write_dst()
