R|M|I = register | memory source | immediate (value)

== control flow ==
JMP  - Jump to address - R|M|I
CALL - JMP to address, push PC to stack - R|M|I
RET  - Load PC from stack and JMP back - no operands
PUSH - Push value to stack - R|M|I
POP  - read out SP - R|M
PUSHF / POPF - flags

== conditionals ==
CMP
TEST

JE/JNE
JG / JGE - signed
JL / JLE - signed
JA / JAE - unsigned
JB / JBE - unsigned
JC / JNC
JO / JNO
JS / JNS

== memory stuff ==
MOV - R|M destination - R|M|I source
XCHG - swap dest/src
WWORD - write 16 bit (big endian) - low byte R|M|I | value R|M|I
RWORD - read 16 bit - address R|M|I - output R|M

== mathematics / logic / bitwise ==
ADD - carry flag
SUB - carry flag
ADC - add with carry
SBC - ^ yea
MUL - discard DWORD
MULH - high byte (?)
DIV - intp 9 for div/0
idiv - signed
REM - R|M|I R|M|I remainder
INC - R
DEC - R
AND - R|M|I, R|M|I so multiple modes
OR -  ^
XOR - ^
NOT - one R|M|I
SHL - R|M|I, R|M|I
SHR - ^
SAR - shift with sign bit
ROL - rotate left unsigned ^
ROR - ^
NEG - two's complement (signed)

==  interrupts   ==
MAKEINTP MODE NUM R|M|I (reserve 0x00-0x0F for hardware)
EDITINTP MODE NUM R|M|I ! removed unnecesary ?
DELINTP NUM r
READINTP NUM R|M - read IVT value
UNINTP - POP flags and PC, JMP to PC
DOINTP NUM - PUSH flags and PC, IRQ lookup

==  sys control  ==
NOP - do nothing
HLT - stop processor until interrupt
CPUID - nothing for now

== flag set + clear + control ==
SETZF / CLZF
SETCF / CLCF
SETOF / CLOF
SETTF / CLTF
SETI / CLI 

GETSP - R|M - stack pointers
SETSP - R|M|I

# TABLE

0x00 - 0x0F > Control flow (7) + jumps (2) (9 used)
0x10 - 0x1F > Mathematics page 1 - Numerical
0x20 - 0x2F > Mathematics page 2 - Bitwise
0x30 - 0x3F > Mathematics page 3 - Signed
0x40 - 0x4F > Reserved for math page 4
0x50 - 0x5F > Normal jump operators
0x60 - 0x6F > Inverted jump operators
0x70 - 0x7F > Unused
0x80 - 0x8F > Unused
0x90 - 0x9F > Unused
0xA0 - 0xAF > Memory management (4 used)
0xB0 - 0xBF > Reserved for future signed stuff
0xC0 - 0xCF > Flag control (12 used)
0xD0 - 0xDF > Interrupts (7 used)
0xE0 - 0xEF > System (Reserved for mode toggles) 
0xF0 - 0xFF > System (3 used)

# OPCODES
0x00 nop | No Operation (Alias)
0x01 jmp | Jump Address
0x02 call | Call Function
0x03 ret | Return
[! 0x04 -> 0x05 ]
0x06 cmp | Compare (SUB)
0x07 test | Test (AND)
[! 0x08 -> 0x09 ]
0x0A push | Push Value To Stack
0x0B pop | Pop From Stack
0x0C pushf | Push Flags
0x0D popf | Pop Flags
[! 0x0E -> 0x0F ]
0x10 inc | Increment
0x11 dec | Decrement
0x12 add | Add
0x13 sub | Subtract
0x14 adc | Add with Carry
0x15 sbc | Subtract with Carry
0x16 div | Divide
0x17 rem | Remainder
0x18 mul | Multiply
0x19 mulh | Multiply, get high byte
[! 0x1A -> 0x1F ]
0x20 and | Bitwise AND
0x21 or  | Bitwise OR
0x22 not | Bitwise NOT
0x23 xor | Bitwise XOR
0x24 shl | Logical Shift Left
0x25 shr | Logical Shift Right
0x26 rol | Bitwise Rotate Left
0x27 ror | Bitwise Rotate Right
[! 0x28 -> 0x2F ]
0x30 neg | Negate (Two's Complement)
0x31 idiv | Integer (Signed) Divide
0x32 imul | Integer (Signed) Multiply
0x33 imulh | Integer (Signed) Mutliply, get high byte
0x34 sar | Arithmetic Shift Right
[! 0x35 -> 0x3F ]
[! 0x40 -> 0x4F ]
0x50 je | Jump if Equal
0x51 jg | Jump if Greater Than
0x52 jge | Jump if Greater or Equal
0x53 ja | Jump if Above (unsigned)
0x54 jae | Jump if Above or Equal (unsigned)
0x55 jc | Jump if Carry Flag
0x56 jo | Jump if Overflow Flag
0x57 js | Jump if Sign Flag
[! 0x58 -> 0x5F ]
0x60 jne | Jump if Not Equal
0x61 jl | Jump if Less Than
0x62 jle | Jump if Less or Equal
0x63 jb | Jump if Below (unsigned)
0x64 jbe | Jump if Below or Equal (unsigned)
0x65 jnc | Jump if Carry Flag Unset
0x66 jno | Jump if Overflow Flag Unset
0x67 jns | Jump if Sign Flag Unset
[! 0x70 -> 0x9F ]
0xA0 mov | Move Value
0xA1 xchg | Exchange Source with Destination
0xA2 wword | Write Word
0xA3 rword | Read Word
[! 0xA4 -> 0xBF ]
0xC0 setzf | Set Zero Flag
0xC1 setcf | Set Carry Flag
0xC2 setof | Set Overflow Flag
0xC3 settf | Set Trap Flag
0xC4 setif | Set Interrupt Flag
0xC5 clzf | Set Zero Flag
0xC6 clcf | Set Carry Flag
0xC7 clof | Set Overflow Flag
0xC8 cltf | Set Trap Flag
0xC9 clif | Set Interrupt Flag
0xCA getsp | Set Stack Pointer
0xCB setsp | Set Stack Pointer
[! 0xCC -> 0xCF ]
0xD0 dointp | Trigger Interrupt
0xD1 unintp | Return from Interrupt
0xD2 makeintp | Create Interrupt
0xD3 unused, reserved for editintp
0xD4 readintp | Read Interrupt To Register
0xD5 delintp | Delete Interrupt
[! 0xD6 -> 0xEF ]
0xF0 nop | No Operation
[! 0xF1 -> 0xFD ]
0xFE cpuid | Get CPU Informations
0xFF halt | Halt Processor
