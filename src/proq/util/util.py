from collections import deque

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
