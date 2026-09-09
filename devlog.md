okay soo I started this project without picking a place to ship it and this happens to be the only program that really fits right now SO! time to devlog 6 hours of work n probs 10h of research!! :x

### devlogs
are gonna have to be really technical :pf: there's not much to screenshot so ill do my best to explain all the concepts im researching!

### processor
this is a 16 bit computer emulator! the root of something this low level is the processor. It being 16 bit means that it works with 16 bit numbers, which are 2 bytes or 4 hex: something like `0x3A33`. All the addresses it can reference and values it can store use 16 bit numbers like this. Opcodes (numbers that represent instructions) are represented in 8 bit blocks, which gives 255 unique instructions, and addresses *contain* 8 bit numbers, or one byte each.

### memory
In the 16 bit space, there are 65,536 memory addresses, ranging from `0x0000` to `0xFFFF`. The `MU()` class (Memory Unit :sho:) lets me assign and access devices on the memory modularly. First, ROM: program memory that can be loaded before execution, but not written to. then, RAM- read-writable, slower than a register (on real hardware), but can hold much more information. The last bit, from the range `0xF000` to `0xFFFF` (4KiB) is reserved for:

### MMIO
or Memory-Mapped Input/Output. The processor is useless if it can't get information or display it to a user, and this is how we do that. The processor can read information from a special memory address, then write to another one to input and output data. This is also the space where some system things can be stored, like the reset bytes or the IVT (Interrupt Vector Table). I'll explain more about those things in a later devlog.

Thanks to Python being okay at OOP, the addresses on this emulated processor can be assigned really easily:
```python
self.keyboard_device = InterruptKeyboard(intp = 0x11) # so it can be used in main.py
self.mu.map_device(0x0000, romsize - 1, ROM(size = romsize, binary = binary))
self.mu.map_device(romsize, romsize + memsize - 1, RAM(size = memsize))
self.mu.map_device(0xF000, 0xF000, StdoutOutput())
self.mu.map_device(0xF001, 0xF001, keyboard_device)
# maybe a screen? or buttons? or GPIO pins? or a nuclear bomb? :3
```
and you might do something like this (i haven't built this part yet):
```python
# print the character in the keyboard's memory to stdout
#      instruction, memory to memory, destination, source 
self.cu.opcode(MOV, 0x08, 0xF000, 0xF001)
```

### Registers
Memory is great, but in real hardware it's slow, and it's weird to assign to and work with. Registers go inside of the processor itself for a place to really quickly keep and modify small amounts of information.

the General Purpose Registers (GPRs) R1 through R12 are used for storing small amounts of information between instructions. There's also the PC, or the Program Counter, which stores the memory address of the current instruction; the `IR`, instruction register, which stores the current opcode; and the SP, which points to a location in memory where the stack currently is, used for functions and interrupts.

Finally, a flags register, encoding single bits important for math instructions that I'll explain later.

### CU, ALU, and the rest of the stuff
Okay so I haven't mentioned a lot of stuff that I've worked on or that need to be considered- i'll explain them in the future. Right now, I'm working on how the processor actually performs instructions, and I'll write about that when the time comes :)

### Goog... :goog:
hopefully this is uh, somewhat educational and doesn't just read as a rant!! the devlogs that Don't take 6 hours are to be a lot more digestible but until then time to go back to OOP hell :droidtehe: also this is like full character limit lmao

=================

see i told you it would only be a few hours :woomy:
today, *while fighting OOP*, i got the cpu reading actual instructions for the first time!
a big explanation, if you're interested:

### the CU
The CU, or Control Unit, is a... *guess...* Unit that Controls Things :droidshocked:
For every tick of the processor, it looks at the Program Counter (PC) register, and reads the byte, or the opcode, in that memory address. It then runs the instruction associated with that 8-bit opcode number, which does whatever it needs to the memory and registers of the processor, using the ALU (Arithmetic Logic Unit) to perform mathematical operations.

Some processors use a large amount of opcodes, but my processor uses more memory space to save on making multiple opcodes for similar functions. For example, if you wanted to `MOV` one value to another place, there are several ways you might want to do it: register to register, register to memory, memory to memory, et cetera. In a modern processor, those would all be represented as distinct opcodes. In my processor (and other older or simpler ones), you use a second byte to specify which form of that operation you're doing.

That second byte is called an operand: an instruction can have multiple that all follow the initial instruction, modifying the behaviour. Following the previous example:
```hex
0x0000: 0x10 # MOV
0x0001: 0x02 # Value to Register
0x0002: 0x04 # Destination: Register R4
0x0003: 0x3A # Source: high byte 
0x0004: 0x33 # Source: low byte
```
this program puts the value 0x3A33 (ASCII for :3) in R4! it can keep performing instructions like this :) those are what I have to implement!

### OOP hell, again
The opcodes are defined centrally in `set.py`, specifically an IntEnum named `Op`. It's just a set of key-value pairs with classes inside, so-
```python
MOV = 0x10
ADD = 0x11
SUB = 0x12
```
and I can change and add this as I keep developing instructions. Each instruction is a class inherited from a base Instruction class, so `ADD(Instruction): etc`. The Instruction base class takes care of adding itself to an internal register of opcodes and their matching classes, and it holds references to one central MU, registers, and ALU. This way, instructions are simply a single function, `execute()`.

That function is an Iterator function returning no values, allowing me to put it inside of a class:
```python
def tick(self):
    if not self.iterable:
        opcode = self.mu.read(self.registers.PC)
        instruction = Instruction.registry.get(opcode)
        instance = instruction(self.mu, self.alu, self.registers)
        self.registers.PC += 0x0001
        self.iterable = instance.execute()
    
    try:
        next(self.iterable)
    except StopIteration:
        self.iterable = None
```
which will perform only one part of the instruction every clock cycle, or tick, mimicing how real processors work!!

### Next
I need to design the first few basic control flow instructions, then I'll probably devlog there. Math instructions come after that, which requires me to learn BINARY OPERATORS AND BOOLEAN MATH OH GOD OH GOD ODGSJHNfhm ,     ,

=================

okay ! i've got most of the instructions I think I should need for now, and that totals to 71 distinct ones. Far from the 256 the processor supports, so that's good! most of them can read or write registers, memory, or an immediate number in the code.

I can always add more later as need be :droidtehe: but now i have to implement them!!

eventually, I'll write an assembler and linker to do this automatically. For now though I'll have to write bytecode manually :fear: also going to assign these to specific opcodes first...
