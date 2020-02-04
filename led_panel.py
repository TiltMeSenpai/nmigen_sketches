from nmigen import *
from nmigen.cli import main
from nmigen_boards import icebreaker
from util.quarter_wave import SinTable
from util.dac import *

import itertools

class Main(Elaboratable):
    def __init__(self):
        self.in_port  = Signal(10, reset = 0xFF)
        self.out_port = Signal(signed(8))

    def elaborate(self, platform):
        def get_all_resources(name):
            resources = []
            for number in itertools.count():
                try:
                    resources.append(platform.request(name, number))
                except:
                    break
            return resources
        leds = [res.o for res in get_all_resources("led")]
        m = Module()
        freq = getattr(platform, "default_clk_frequency", 10000)
        out_shift = Signal(8)
        blinky = Signal()

        self.ctr = Signal(range(0, int(freq//60)), reset=int(freq//60 - 1))

        m.submodules.quarter_wave = SinTable(self.in_port, self.out_port)
        m.submodules.pwm = PWM(out_shift, blinky)

        m.d.comb += out_shift.eq(self.out_port + (2 ** (out_shift.width - 1)))
        m.d.comb += Cat(leds).eq(Repl(blinky, len(leds)))

        m.d.sync += [
            self.ctr.eq(self.ctr - 1)
        ]
        with m.If(self.ctr == 0):
            m.d.sync += self.ctr.eq(self.ctr.reset)
            m.d.sync += self.in_port.eq(self.in_port + 1)
        return m

if __name__ == "__main__":
    m = Main()
    board = icebreaker.ICEBreakerPlatform()
    board.add_resources(board.break_off_pmod)
    board.build(m)
    # main(m, ports = [m.in_port, m.out_port])
