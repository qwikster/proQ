from enum import IntEnum


_hex = hex
def hex(val: int, pad: int = 4) -> str:
    sign = "-" if val < 0 else ""
    return f"{sign}0x{abs(val):0{pad}X}"

class MutableInt:
    def __init__(self, value: int = 0):
        self.value = value

    def set(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __int__(self):
        return self.value

    def __index__(self):
        return self.value

class TypeOperand(IntEnum):
    IMMEDIATE = 0
    REGISTER  = 1
    MEMORY_DR = 2 # direct [Addr]
    MEMORY_ID = 3 # indirect [Reg]

class RegisterOperand(IntEnum):
    REG_0 = 0
    REG_1 = 1
    REG_2 = 2
    REG_3 = 3
    REG_4 = 4
    REG_5 = 5
    REG_6 = 6
    REG_7 = 7
    REG_8 = 8
    REG_9 = 9
    REG_10 = 10
    REG_11 = 11
    REG_PC = 12
    REG_IR = 13
    REG_SP = 14
    REG_FLAG = 15
