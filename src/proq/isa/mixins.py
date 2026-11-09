from typing import Protocol

from proq.isa.base import IsInstruction


class IsStackInstruction(IsInstruction, Protocol): #IsInstruction should only apply to subclasses of Instruction
    def push(self, value: int) -> None: ...
    def pop(self) -> int: ...
