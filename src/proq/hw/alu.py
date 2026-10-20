from enum import IntEnum

from proq.hw.register import Registers
from proq.util.exceptions import InstructionNotImplementedError

# i'm so sorry anyone that needs to figure this out, i'm too stupid to actually understand this, I just implemented x86's rules, best of luck to ye

class Ops(IntEnum):
    AND = 0x0
    OR  = 0x1
    XOR = 0x2
    NOT = 0x3
    ADD = 0x4
    SUB = 0x5
    SHL = 0x6
    SHR = 0x7
    ROL = 0x8
    ROR = 0x9
    NEG = 0xA
    SAR = 0xB

class ALU:
    def __init__(self, registers: Registers, size: int = 0x10): # 16bit
        self.reg = registers
        self.flags = self.reg.flags
        self.size = size
        self.mask = (1 << self.size) - 1
        self.sign_bit = 1 << (self.size - 1)

    def logical_flags(self, result):
        self.flags.CF = False
        self.flags.OF = False
        self.flags.ZF = result == 0x0000
        self.flags.SF = bool(result & self.sign_bit)

    def do(self, op: Ops, a: int, b: int) -> int:
        match op:
            case Ops.AND:
                result = a & b
                self.logical_flags(result)

            case Ops.OR:
                result = a | b
                self.logical_flags(result)

            case Ops.XOR:
                result = a ^ b
                self.logical_flags(result)

            case Ops.NOT:
                result = ~a
                self.logical_flags(result)

            case Ops.ADD:
                num = a + b
                result = num & self.mask

                self.flags.CF = num > self.mask
                self.flags.OF = bool(((a ^ result) & (b ^ result)) & self.sign_bit)
                self.flags.ZF = result == 0x0000
                self.flags.SF = bool(result & self.sign_bit)

            case Ops.SUB:
                num = a - b
                result = num & self.mask

                self.flags.CF = b > a
                self.flags.OF = bool(((a ^ b) & (a ^ result)) & self.sign_bit)
                self.flags.ZF = result == 0x0000
                self.flags.SF = bool(result & self.sign_bit)

            case Ops.SHL:
                if b == 0:
                    return a

                result = (a << b) & self.mask

                msb_mask = 1 << (self.size - 1)
                self.flags.SF = bool(result & msb_mask)
                self.flags.ZF = (result == 0)
                self.flags.CF = bool((a >> (self.size - b)) & 1) if b <= self.size else False
                self.flags.OF = (self.flags.SF != self.flags.CF) if b == 1 else False

            case Ops.SHR:
                if b == 0:
                    return a

                result = (a >> b) & self.mask

                self.flags.CF = bool((a >> (b - 1)) & 1) if b <= self.size else False
                self.flags.SF = False
                self.flags.ZF = (result == 0)
                self.flags.OF = bool(a & (1 << (self.size - 1))) if b == 1 else False

            case Ops.ROL:
                shift = b % self.size

                if b == 0 or shift == 0:
                    return a

                high = (a << shift) & self.mask
                low = (a >> (self.size - shift)) & self.mask
                result = high | low

                self.flags.CF = bool(result & 1)

                if b == 1:
                    msb = 1 << (self.size - 1)
                    self.flags.OF = bool(result & msb) != self.flags.CF
                else:
                    self.flags.OF = False

            case Ops.ROR:
                shift = b % self.size

                if b == 0 or shift == 0:
                    return a

                high = (a >> shift) & self.mask
                low = (a << (self.size - shift)) & self.mask
                result = low | high

                msb = 1 << (self.size - 1)
                self.flags.CF = bool(result & msb)

                if b == 1:
                    self.flags.OF = bool(result & msb) != bool(result & (1 << (self.size - 2)))
                else:
                    self.flags.OF = False

            case Ops.NEG: # two's complement
                self.flags.CF = (a != 0)
                result = (-a) & self.mask

                msb = 1 << (self.size - 1)
                self.flags.SF = bool(result & msb)
                self.flags.ZF = (result == 0)
                self.flags.OF = bool(a & msb) and bool(result & msb)

            case Ops.SAR:
                if b == 0:
                    return a

                if b <= self.size:
                    self.flags.CF = bool((a >> (b - 1)) & 1)
                else:
                    self.flags.CF = bool(a & (1 << (self.size - 1)))

                neg = bool(a & (1 << (self.size - 1)))

                if neg:
                    padding = (self.mask << (self.size - min(b, 16))) & self.mask
                    result = (a >> b) | padding
                else:
                    result = (a >> b) & self.mask

                self.flags.SF = neg
                self.flags.ZF = (result == 0)
                self.flags.OF = False

            case _:
                return InstructionNotImplementedError(f"operation {op} not found :(")

        return result & self.mask
