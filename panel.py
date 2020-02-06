from nmigen import *
from nmigen.cli import main
from nmigen_boards import icebreaker
from util.quarter_wave import SinTable
from util.dac import *
from addons.led_panel import PanelDriver,led_driver

import itertools

class Main(Elaboratable):
    def elaborate(self, platform):
        m = Module()
        m.submodules.panel = PanelDriver()
        return m

if __name__ == "__main__":
    m = Main()
    board = icebreaker.ICEBreakerPlatform()
    board.add_resources(board.break_off_pmod)
    board.add_resources([led_driver()])
    board.build(m)
    # main(m, platform=board, ports = [])
