from enum import IntEnum


# centralized operation definitions
class Op(IntEnum):
    NOP_ALIAS = 0x00
    JMP = 0x01
    CALL = 0x02
    RET = 0x03

    # CMP
    # TEST

    PUSH = 0x0A
    POP = 0x0B
    PUSHF = 0x0C
    POPF = 0x0D

    MOV = 0xA0

    NOP = 0xF0
    CPUID = 0xFE
    HALT = 0xFF
