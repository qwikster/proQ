from enum import IntEnum


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
    def do(self, op: Ops, a: int, b: int) -> int:
        match op:
            case Ops.AND:
                result =  a & b
            case Ops.OR:
                result = a | b
            case Ops.XOR:
                result = a ^ b
            case Ops.NOT:
                result = ~a
            case Ops.ADD:
                result = a + b
            case Ops.SUB:
                result = a - b
            case Ops.SHL:
                result = a << b
            case Ops.SHR:
                result = a >> b
            case Ops.ROL:
                result = a << b | a >> (16 - b)
            case Ops.ROR:
                result = a >> b | a << (16 - b)
            case Ops.NEG: # two's complement
                result = (1 << 16) - a
            case Ops.SAR:
                result = a >> b | a << (16 - b)
        return result & 0xFFFF # keep as 16 bit
