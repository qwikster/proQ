from proq.hw.alu import Ops
from proq.isa.mixins import BasicMathInstruction

# class AND(BasicMathInstruction):
#     op = Ops.AND
#
# i could just copy paste that but instead here have some Sexy OOP Logic

for name in ("AND", "OR", "NOT", "XOR", "SHL", "SHR", "ROL", "ROR"):
    globals()[name] = type(name, (BasicMathInstruction,), {"op": getattr(Ops, name)})
