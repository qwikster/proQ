import argparse

from proq.cpu import CPU
from proq.util.logging import Logger


def entry():
    parser = argparse.ArgumentParser(description="shitass cpu emulator")
    parser.add_argument("binary", type=str, help = "machine code to run")
    parser.add_argument("--memsize", "--mem", "-m", type=int, default = 4096, help = "size of RAM in bytes")
    parser.add_argument("--romsize", "--rom", "-r", type=int, default = 57344, help = "size of ROM in bytes")
    parser.add_argument("--reset", "--start", "-s", type=int, default = 0, help = "memory address containing start of program")

    args = parser.parse_args()

    if not args.binary:
        binary = bytes(0)
    else:
        with open(args.binary, 'rb') as f:
            binary = f.read()

    logger = Logger(default = True, stdout = True, setup = True)
    logger.setup("logger started")

    cpu = CPU(
        binary = binary,
        logger = logger,
        memsize = args.memsize,
        romsize = args.romsize,
        flag_debug = True
    )

    logger.setup("starting CPU")

    while True:
        check_io(cpu)
        cpu.tick()

def check_io(cpu: CPU):
    pass # check keyboard and display to screen here
