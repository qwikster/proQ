import pygame

from proq.hw.mu import MemoryDevice
from proq.util.exceptions import EmulatorMemoryError

# 0: mode byte (push here to render)
# 1: color byte
# 2: get time since last frame in ms
# 3: get frame number
# 4: x0
# 5: y0
# 6: x1/width
# 7: y1/height

class Screen(MemoryDevice):
    def __init__(self, size: tuple[int, int]):
        pygame.init()
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption("proQ")
        self.clock = pygame.time.Clock()

    def read(self, addr: int) -> int:
        return 0

    def write(self, addr: int, value: int):
        match addr:
            case 0x0000:
                pass
            case 0x0001:
                pass

    def render(self):
        pygame.display.flip()
        self.clock.tick(60)
