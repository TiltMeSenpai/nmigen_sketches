from nmigen import *
from nmigen.build import *
from enum import Enum

def led_driver(instance = 0, pmod_1 = 0, pmod_2 = 1):
    return Resource("led_panel", instance,
                    Subsignal("panel_r", Pins(
                        "1 7", dir="o", conn=("pmod", 0))),
                    Subsignal("panel_g", Pins(
                        "2 8", dir="o", conn=("pmod", 0))),
                    Subsignal("panel_b", Pins(
                        "3 9", dir="o", conn=("pmod", 0))),
                    Subsignal("panel_x", Pins(
                        "4 10", dir="o", conn=("pmod", 0))),
                    Subsignal("panel_addr", Pins(
                        "1 2 3 4 10", dir="o", conn=("pmod", pmod_2))),
                    Subsignal("panel_bl", Pins(
                        "7", dir="o", conn=("pmod", pmod_2))),
                    Subsignal("panel_la", Pins(
                        "8", dir="o", conn=("pmod", pmod_2))),
                    Subsignal("panel_ck", Pins(
                        "9", dir="o", conn=("pmod", pmod_2)))
    )

class PanelDriver(Elaboratable):
    class LED_FSM(Enum):
        INIT = 0
        BLANK = 1
        CLK_OUT = 2
        LATCH_HOLD = 3
    def elaborate(self, platform):
        m = Module()
        state = Signal(self.LED_FSM)
        state_cnt = Signal(range(0, 64), reset=63)
        led_panel = platform.request("led_panel")
        with m.Switch(state):
            with m.Case(self.LED_FSM.INIT):
                m.d.sync += [
                    led_panel.panel_addr.eq(0),
                    led_panel.panel_r.eq(0b11),
                    led_panel.panel_g.eq(0b00),
                    led_panel.panel_b.eq(0b11),
                    led_panel.panel_ck.eq(0),
                    led_panel.panel_la.eq(0),
                    led_panel.panel_bl.eq(1),
                    state_cnt.eq(4),
                    state.eq(self.LED_FSM.BLANK)
                ]
            with m.Case(self.LED_FSM.BLANK):
                with m.If(state_cnt == 0):
                    m.d.sync += [
                        led_panel.panel_bl.eq(0),
                        state_cnt.eq(state_cnt.reset),
                        state.eq(self.LED_FSM.CLK_OUT)
                    ]
                with m.Else():
                    m.d.sync += [
                        state_cnt.eq(state_cnt - 1),
                        led_panel.panel_bl.eq(1)
                    ]
            with m.Case(self.LED_FSM.CLK_OUT):
                with m.If(led_panel.panel_ck == 0):
                    with m.If(state_cnt == 0):
                        m.d.sync += [
                            state_cnt.eq(4),
                            state.eq(self.LED_FSM.LATCH_HOLD)
                        ]
                    with m.Else():
                        m.d.sync += [
                            led_panel.panel_ck.eq(1),
                            led_panel.panel_r.eq(~led_panel.panel_r),
                            led_panel.panel_g.eq(~led_panel.panel_g),
                            led_panel.panel_b.eq(~led_panel.panel_b),
                            state_cnt.eq(state_cnt - 1)
                        ]
                with m.Else():
                    m.d.sync += led_panel.panel_ck.eq(0)
            with m.Case(self.LED_FSM.LATCH_HOLD):
                with m.If(state_cnt == 1):
                    m.d.sync += [
                        led_panel.panel_la.eq(0),
                        state_cnt.eq(4),
                        state.eq(self.LED_FSM.BLANK)
                    ]
                with m.Else():
                    m.d.sync += [
                        led_panel.panel_la.eq(1),
                        led_panel.panel_addr.eq(led_panel.panel_addr + 1),
                        state_cnt.eq(state_cnt - 1),
                    ]
        return m
