#!/usr/bin/env python

"""
    Eine kleine Demo für ein FT2232HL-USB-Board mit RGB-LEDs.

    BDBUS6 -> schwarz -> A
    BDBUS5 -> weiß -> B
    BDBUS4 -> grau -> S
"""

import colorsys
import time

from pyftdi.gpio import GpioController, GpioException


class Incremental_rotary_encoder:

    def __init__(self, cw_callback=None, ccw_callback=None,
                       switch_callback=None, count_callback=None):
        self.cw_callback = cw_callback
        self.ccw_callback = ccw_callback
        self.switch_callback = switch_callback
        self.count_callback = count_callback

        self._prev_lvl_A = None
        self._prev_lvl_B = None
        self._prev_lvl_S = None

        self.count = 0
        self.min = 0
        self.max = 100

    def update(self, lvl_A, lvl_B, lvl_S):
        if self._prev_lvl_S is None:
            self._prev_lvl_S = lvl_S
        elif self._prev_lvl_S and not lvl_S:
            self.switch_callback()
        self._prev_lvl_S = lvl_S

        if self._prev_lvl_A is None:
            self._prev_lvl_A = lvl_A
            self._prev_lvl_B = lvl_B
        elif self._prev_lvl_A != lvl_A:
            if lvl_A == lvl_B:
                self.count = max(self.min, self.count - 1)
                if self.ccw_callback is not None:
                    self.ccw_callback()
            else:
                self.count = min(self.max, self.count + 1)
                if self.cw_callback is not None:
                    self.cw_callback()
            if self.count_callback is not None:
                self.count_callback(self.count)
        self._prev_lvl_A = lvl_A


def on_count(count):
    print(count)


def on_switch():
    global v
    if v == 1.0:
        v = 0.5
    else:
        v = 1.0


port_BD = GpioController()
port_BD.open_from_url('ftdi://ftdi:0x6010/2', direction=0x07)


my_encoder = Incremental_rotary_encoder(
    switch_callback=on_switch, count_callback=on_count)


v = 1.0
pwm_counter = 0


while True:
    portval = port_BD.read_port()
    lvl_A = ((portval >> 6) & 1) != 0
    lvl_B = ((portval >> 5) & 1) != 0
    lvl_S = ((portval >> 4) & 1) != 0

    my_encoder.update(lvl_A, lvl_B, lvl_S)

    h = my_encoder.count / 100.0

    r, g, b = colorsys.hsv_to_rgb(h, 1, v)

    if pwm_counter < 100:
        pwm_counter = pwm_counter + 1
    else:
        pwm_counter = 1

    if pwm_counter <= r * 100:
        rb = 1
    else:
        rb = 0

    if pwm_counter <= g * 100:
        gb = 1
    else:
        gb = 0

    if pwm_counter <= b * 100:
        bb = 1
    else:
        bb = 0

    portval = ~((gb << 2) | (rb << 1) | (bb << 0)) & 0x07

#    print(f"\r{my_encoder.count} / 100 = {h} -> {r}, {g}, {b} -> {portval:03b}", end="")

    port_BD.write_port(portval)
