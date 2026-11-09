from collections.abc import Iterator

from proq.isa.base import Instruction


class MOV(Instruction):
    def execute(self) -> Iterator[None]:
        self.decode_mode_bytes()
        yield

        value = self.get_src_val()
        yield

        self.write_dst(value)
        self.pcio()
        yield
