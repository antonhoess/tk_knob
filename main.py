#!/usr/bin/env python

from typing import Optional
import tkinter as tk

from tk_knob import Knob


class KnobTest:
    def __init__(self):
        knob_size = 80
        window_width = 250
        window_height = 250
        self._master = tk.Tk()
        self._master.title("KnobTest")
        self._master.geometry(f"{window_width}x{window_height}")

        # A knob
        self._knb = Knob(self._master, size=knob_size, knob_radius=.8, left_value_limit=0, right_value_limit=100,
                         value=30, zero_position_angle=250, angle_value_factor=100 / 320, step_size=1,
                         turn_type=Knob.TurnType.ANGLE)
        self._knb.place(x=(window_width - knob_size) / 2, y=(window_height - knob_size) / 2)
        self._knb.bind("<<ValueChange>>", self._on_value_change)

        # A label showing the current value
        self._lbl_value = tk.Label(self._master)
        self._lbl_value.place(x=(window_width - knob_size) / 2 + 20, y=(window_height - knob_size) / 2 + knob_size)
    # end def

    def _on_value_change(self, _event: Optional[tk.Event] = None):
        self._lbl_value.configure(text=f"{self._knb.value :.2f}")
        self._master.attributes("-alpha", self._knb.value / 100 / 2 + .5)
    # end def

    def run(self) -> None:
        self._on_value_change()

        tk.mainloop()
    # end def
# end class


def main():
    knob_test = KnobTest()
    knob_test.run()
# end def


if __name__ == "__main__":
    main()
# end if
