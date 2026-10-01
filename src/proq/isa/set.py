from enum import IntEnum


# centralized operation definitions
class Op(IntEnum):
    NOP_ALIAS = 0x00



    NOP = 0xF0
    CPUID = 0xFE
    HALT = 0xFF
