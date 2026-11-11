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

    INC = 0x10
    DEC = 0x11
    ADD = 0x12
    SUB = 0x13
    # adc sbc div rem mul mulh

    AND = 0x20
    OR = 0x21
    NOT = 0x22
    XOR = 0x23
    SHL = 0x24
    SHR = 0x25
    ROL = 0x26
    ROR = 0x27

    # neg idiv imul imulh sar

    MOV = 0xA0

    NOP = 0xF0
    BREAK = 0xF1
    CPUID = 0xFE
    HALT = 0xFF
