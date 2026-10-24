from collections import deque
from enum import IntEnum

from proq.util.exceptions import InvalidModeByteError

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

class Interrupts:
    def __init__(self, value: int = 0):
        self.queue = deque()

    def new(self, value: int):
        self.queue.append(value)

    def get(self):
        return self.queue.popleft()

    def check_hw(self):
        if len(self.queue) == 0:
            return False
        return self.queue[0] <= 0x0F

    def __len__(self):
        return len(self.queue)

    def __call__(self, value: int):
        self.new(value)

class TypeOperand(IntEnum):
    IMMEDIATE = 0
    REGISTER  = 1
    MEMORY_DR = 2 # direct [Addr]
    MEMORY_ID = 3 # indirect [Reg]

class RegisterOperand(IntEnum):
    # also used for immediate value size signalling
    REG_0 = 0
    REG_1_BYTE = 1
    REG_2_WORD = 2
    REG_3 = 3
    REG_4_DWORD = 4
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

def decode_mode_bytes(byte: int, reg: bool = False) -> tuple[TypeOperand, TypeOperand, bool] | tuple[RegisterOperand, RegisterOperand, bool]:
    dst = (byte >> 4) & 0b1111 # left (upper) bytes
    src = byte & 0b1111 # right (lower) bytes
    if not reg:
        if dst >= len(TypeOperand) or src >= len(TypeOperand):
            raise InvalidModeByteError
        needs_reg_byte = dst in (0, 1, 3) or src in (0, 1, 3)
        return (TypeOperand(dst), TypeOperand(src), needs_reg_byte)
    else:
        return (RegisterOperand(dst), RegisterOperand(src), True)
