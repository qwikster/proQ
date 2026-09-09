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
MUL - discard DWORD or write to memory
MULH - high byte (?)
DIV - intp 9 for div/0
MOD - R|M|I R|M|I modulo
INC - R
DEC - R
AND - R|M|I, R|M|I so multiple modes
OR -  ^
XOR - ^
NOT - one R|M|I
SHL - R|M|I, R|M|I
SHR - ^
SAL - shift with sign bit
SHR
ROL - ^
ROR - ^
NEG - two's complement

==  interrupts   ==
MAKEINTP MODE NUM R|M|I (reserve 0x00-0x0F for hardware)
EDITINTP MODE NUM R|M|I
DELINTP NUM
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
