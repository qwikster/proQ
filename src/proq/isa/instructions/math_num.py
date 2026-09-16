from proq.isa.base import Instruction


class ADD(Instruction):
    def execute(self):
        self.registers.PC += 0x01 # ONLY FOR OPERANDS the first one is done
        yield

class SUB(Instruction):
    def execute(self):
        self.registers.PC += 0x01
        yield
