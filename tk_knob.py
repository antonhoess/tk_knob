from __future__ import annotations
from typing import Tuple, Optional
import tkinter as tk
import math


class Knob(tk.Canvas):
    class MarkerType:
        NONE = 1
        LINE = 2
        CIRCLE = 3
    # end class

    class TurnType:
        HORIZONTAL = 1
        VERTICAL = 2
        DIST = 3
        ANGLE = 4
    # end class

    def __init__(self, master: tk.Misc, size: int, knob_radius: float,
                 left_value_limit: Optional[float], right_value_limit: Optional[float], value: float,
                 zero_position_angle: float = 0, angle_value_factor: float = 1, step_size: float = 1,
                 turn_type: TurnType = TurnType.HORIZONTAL,
                 **kwargs):
        super().__init__(master, **kwargs)

        self._draw_inited = None

        self.configure(width=size, height=size)

        self._size = size
        self.knob_radius = knob_radius

        self._zero_position_angle = zero_position_angle / 180 * math.pi  # XXX Add as property.
        self._left_value_limit = None
        self._right_value_limit = None
        self.left_value_limit = left_value_limit
        self.right_value_limit = right_value_limit
        self._angle_value_factor = angle_value_factor / math.pi * 180  # XXX Add as property.
        self._dist_angle_factor = 1 / 180 * math.pi  # XXX  Add as property and parameter?
        self._value = None
        self._angle = None
        self.value = value
        self.step_size = step_size
        self.turn_type = turn_type

        self._ring_radius = knob_radius + .1  # XXX  Add as property and parameter?
        self._marker_type = Knob.MarkerType.NONE
        self._marker_oid = None

        # Turn mode
        self._turn_mode = False
        self._turn_start_pos_x = None
        self._turn_start_pos_y = None
        self._turn_start_dist = None
        self._turn_start_angle = None
        self._turn_last_angle = None
        self._turn_start_angle_mouse = None
        self._turn_full_angles = None

        # Bind events
        self.bind("<Button-1>", self._on_button_1)
        self.bind("<B1-Motion>", self._on_b1_motion)
        self.bind("<ButtonRelease-1>", self._on_button_release_1)

        # Draw the widget - it only gets modified later on
        self._draw_inited = False
        self._draw_marker = None
        self._draw()
    # end def

    def _on_button_1(self, event: tk.Event) -> None:
        x = getattr(event, "x")
        y = getattr(event, "y")

        if self._is_point_in_radius(x, y, self._knob_radius):
            self._turn_mode = True
            self._turn_start_pos_x, self._turn_start_pos_y = self.winfo_pointerxy()
            self._turn_start_dist = self._get_mouse_dist()
            self._turn_start_angle = self._angle
            print(self._angle)
            self._turn_start_angle_mouse = self._get_mouse_angle()
            self._turn_full_angles = 0
            # end if
    # end def

    def _on_b1_motion(self, _event: tk.Event) -> None:
        if self._turn_mode:
            if self._turn_type is Knob.TurnType.HORIZONTAL:
                angle = self._turn_start_angle + \
                        (self.winfo_pointerx() - self._turn_start_pos_x) * self._dist_angle_factor
                self.value = self._get_limited_value(self._angle2value(angle))
                self._angle = self._value2angle(self._value)

            elif self._turn_type is Knob.TurnType.VERTICAL:
                angle = self._turn_start_angle + \
                        (self.winfo_pointery() - self._turn_start_pos_y) * self._dist_angle_factor
                self.value = self._get_limited_value(self._angle2value(angle))
                self._angle = self._value2angle(self._value)

            elif self._turn_type is Knob.TurnType.DIST:
                dist_diff = self._get_mouse_dist() - self._turn_start_dist
                angle = self._turn_start_angle + dist_diff * self._dist_angle_factor
                self.value = self._get_limited_value(self._angle2value(angle))
                self._angle = self._value2angle(self._value)

            elif self._turn_type is Knob.TurnType.ANGLE:
                cur_angle = self._get_mouse_angle()

                if self._turn_last_angle is not None:
                    # Did we cross the 0 / 2*pi border? In which direction?
                    if cur_angle < .5 * math.pi and self._turn_last_angle > 1.5 * math.pi:
                        self._turn_full_angles += 1
                    elif cur_angle > 1.5 * math.pi and self._turn_last_angle < .5 * math.pi:
                        self._turn_full_angles -= 1
                    # end if
                # end if

                turned_angle = cur_angle + self._turn_full_angles * 2 * math.pi - self._turn_start_angle_mouse
                self._turn_last_angle = cur_angle  # Set new value as old value
                angle = self._turn_start_angle + turned_angle

                self.value = self._get_limited_value(self._angle2value(angle))
                self._angle = self._value2angle(self._value)
            # end if
        # end if
    # end def

    def _on_button_release_1(self, _event: tk.Event) -> None:
        self._turn_mode = False
    # end def

    def _is_point_in_radius(self, x: int, y: int, radius: float) -> bool:
        if not 0 < radius <= 1:
            raise ValueError(f"Parameter radius ({radius}) needs to be > 0 and <= 1.")

        else:
            dist = math.hypot(x - self._size / 2, y - self._size / 2)
            point_radius = dist / (self._size / 2)

            return point_radius <= radius
        # end if
    # end def

    def _get_radius_in_pixels(self, radius: float) -> int:
        if not 0 < radius <= 1:
            raise ValueError(f"Parameter radius ({radius}) needs to be > 0 and <= 1.")

        else:
            return int(radius * self._size / 2)
        # end if
    # end def

    def _get_radius_from_pixels(self, radius: int) -> float:
        if not 0 < radius <= self._size:
            raise ValueError(f"Parameter radius ({radius}) needs to be > 0 and <= size.")

        else:
            return (2 * radius) / self._size
        # end if
    # end def

    def _get_coords_by_radius(self, radius: float) -> Tuple[int, int, int, int]:
        if not 0 < radius <= 1:
            raise ValueError(f"Parameter radius ({radius}) needs to be > 0 and <= 1.")

        else:
            x1 = self._get_radius_in_pixels((1 - radius))
            y1 = x1
            x2 = self._size - x1
            y2 = x2

            return x1, y1, x2, y2
        # end if
    # end def

    def _get_mouse_angle(self):
        x_diff = self.winfo_pointerx() - (self.winfo_rootx() + self._size / 2)
        y_diff = self.winfo_pointery() - (self.winfo_rooty() + self._size / 2)
        angle = math.atan2(y_diff, x_diff)

        # Keep the angle between 0..2*pi instead of -pi..pi
        if angle < 0:
            angle = 2 * math.pi + angle
        # end if

        return angle
    # end def

    def _get_mouse_dist(self):
        dist = math.dist(self.winfo_pointerxy(),
                         (self.winfo_rootx() + self._size / 2,
                          self.winfo_rooty() + self._size / 2))

        return dist
    # end def

    def _angle2value(self, angle: float) -> float:
        return angle * self._angle_value_factor
    # end def

    def _value2angle(self, value: float) -> float:
        return value / self._angle_value_factor
    # end def

    def _value_within_limits(self, value: float) -> bool:
        if self._left_value_limit is not None and value < self._left_value_limit:
            return False

        elif self._right_value_limit is not None and value > self._right_value_limit:
            return False

        else:
            return True
        # end if
    # end def

    def _get_limited_value(self, value: float) -> float:
        if self._left_value_limit is not None:
            value = max(self._left_value_limit, value)
        # end if

        if self._right_value_limit is not None:
            value = min(self._right_value_limit, value)
        # end if

        return value
    # end def

    def _draw(self):
        def get_line_marker_coords():
            coords = list()
            angle = self._angle - self._zero_position_angle
            coords.append(self._size / 2 + math.cos(-angle) * self._get_radius_in_pixels(self._knob_radius * .7))
            coords.append(self._size / 2 - math.sin(-angle) * self._get_radius_in_pixels(self._knob_radius * .7))
            coords.append(self._size / 2 + math.cos(-angle) * self._get_radius_in_pixels(self._knob_radius))
            coords.append(self._size / 2 - math.sin(-angle) * self._get_radius_in_pixels(self._knob_radius))

            return coords
        # end def

        if self._draw_inited is not None:
            if not self._draw_inited:
                self._draw_inited = True

                # Ring
                colors = ("yellow", "orange", "red")
                for i, color in enumerate(colors):
                    radius = self._get_radius_from_pixels(self._get_radius_in_pixels(self._knob_radius) + (len(colors) - i) + 1)
                    self.create_oval(*self._get_coords_by_radius(radius), outline=color, width=2)
                # end for

                # Knob
                self.create_oval(*self._get_coords_by_radius(self._knob_radius), fill="black")

                # Light reflection arc
                self.create_arc(*self._get_coords_by_radius(self._knob_radius * .9), outline="light gray", style=tk.ARC,
                                start=30, extent=170)

                # Marker
                self._draw_marker = self.create_line(*get_line_marker_coords(), fill="white", width=3)

            else:
                self.coords(self._draw_marker, *get_line_marker_coords())
            # end if
        # end if
    # end def

    @property
    def knob_radius(self) -> float:
        return self._knob_radius
    # end def

    @knob_radius.setter
    def knob_radius(self, value: float) -> None:
        if not 0 < value <= 1:
            raise ValueError(f"Parameter knob_value ({value}) needs to be > 0 and <= 1.")
        else:
            self._knob_radius = value
        # end if
    # end def

    @property
    def left_value_limit(self) -> Optional[float]:
        return self._left_value_limit
    # end def

    @left_value_limit.setter
    def left_value_limit(self, value: Optional[float]) -> None:
        if self._right_value_limit is not None and value == self._right_value_limit:
            raise ValueError(f"Parameter left_value_limit ({value}) needs "
                             f"to be != right_value_limit ({self._right_value_limit}).")
        else:
            self._left_value_limit = value
        # end if
    # end def

    @property
    def right_value_limit(self) -> Optional[float]:
        return self._right_value_limit
    # end def

    @right_value_limit.setter
    def right_value_limit(self, value: Optional[float]) -> None:
        if self._left_value_limit is not None and value == self._left_value_limit:
            raise ValueError(f"Parameter right_value_limit ({value}) needs "
                             f"to be != left_value_limit ({self._left_value_limit}).")
        else:
            self._right_value_limit = value
        # end if
    # end def

    @property
    def value(self) -> float:
        return self._value
    # end def

    @value.setter
    def value(self, value: float) -> None:
        if not self._value_within_limits(value):
            raise ValueError(f"Parameter value ({value}) needs "
                             f"to be between left_value_limit ({self._left_value_limit}) "
                             f"and right_value_limit ({self._right_value_limit}).")
        else:
            if value != self._value:
                self._value = value
                self._angle = self._value2angle(self._value)  # Keep value and angle synchronous
                self._draw()
                self.event_generate("<<ValueChange>>")
            # end if
        # end if
    # end def

    @property
    def step_size(self) -> float:
        return self._step_size
    # end def

    @step_size.setter
    def step_size(self, value: float) -> None:
        if value == 0:
            raise ValueError(f"Parameter step_size ({value}) needs to be != 0.")
        else:
            self._step_size = value
        # end if
    # end def

    @property
    def turn_type(self) -> TurnType:
        return self._turn_type
    # end def

    @turn_type.setter
    def turn_type(self, value: TurnType) -> None:
        self._turn_type = value
    # end def
# end class
