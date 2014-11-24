from .widget import Widget, BGUI_HORIZONTAL_SCROLLBAR, BGUI_VERTICAL_SCROLLBAR, BGUI_DEFAULT, \
                    BGUI_MOUSE_NONE, BGUI_MOUSE_RELEASE
from .frame import Frame


class Scrollbar(Widget):
    """Scrollbar widget.

    Use the on_scroll attribute to call a function when the scrollbar is slid.

    The slider is the component that moves, the slot is the track it lies in."""
    theme_section = 'Scrollbar'
    theme_options = {'SlotColor1': (0, 0, 0, 0),
                     'SlotColor2': (0, 0, 0, 0),
                     'SlotColor3': (0, 0, 0, 0),
                     'SlotColor4': (0, 0, 0, 0),
                     'SlotBorderSize': 0,
                     'SlotBorderColor': (0, 0, 0, 0),
                     'SliderColor1': (0, 0, 0, 0),
                     'SliderColor2': (0, 0, 0, 0),
                     'SliderColor3': (0, 0, 0, 0),
                     'SliderColor4': (0, 0, 0, 0),
                     'SliderBorderSize': 0,
                     'SliderBorderColor': (0, 0, 0, 0)
                     }

    def __init__(self, parent, name, direction=BGUI_VERTICAL_SCROLLBAR, slider_size=0.1, aspect=None, 
                size=[1, 1], pos=[0, 0], sub_theme='', options=BGUI_DEFAULT):
        """
        :param parent: the widget's parent
        :param name: the name of the widget
        :param direction: specify whether the scollbar is to run horizontally or vertically
        :param aspect: constrain the widget size to a specified aspect ratio
        :param size: a tuple containing the width and height
        :param pos: a tuple containing the x and y position
        :param sub_theme: name of a sub_theme defined in the theme file (similar to CSS classes)
        :param options: various other options

        """
        Widget.__init__(self, parent, name, aspect, size, pos, sub_theme, options)

        self._slot = Frame(self, name + '_slot', pos=[0, 0], size=[1.0, 1.0])
        self._slot.on_click = lambda _: setattr(self, '_slot_clicked', True)

        self._slider = Frame(self._slot, name + '_slider', pos=[0, 0], size=[1.0, 1.0])
        self._slider.on_click = lambda _: setattr(self, '_slider_clicked', True)

        self._slot.colors = [list(self.theme['SlotColor{}'.format(i + 1)]) for i in range(4)]
        self._slider.colors = [list(self.theme['SliderColor{}'.format(i + 1)]) for i in range(4)]

        self._slider.border = self.theme['SliderBorderSize']
        self._slot.border = self.theme['SlotBorderSize']
        self._slider.border_color = self.theme['SliderBorderColor']
        self._slot.border_color = self.theme['SliderBorderColor']

        self.direction = direction
        self._progress = 0.0

        self._snap_range = None
        self._slider_clicked = False
        self._slider_offset = None
        self._slot_clicked = False
        self._on_scroll = None  # on_finished for when the slider is moving

        self.slider_size = slider_size

    @property
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = progress = max(min(value, 1), 0)

        position = [0.0, 0.0]
        position[self.direction] = min(1, max(0, progress))
        self._slider.position = position

    @property
    def on_scroll(self):
        """Callback while the slider is being slid."""
        return self._on_scroll

    @on_scroll.setter
    def on_scroll(self, on_scroll):
        self._on_scroll = on_scroll

    @property
    def slider_size(self):
        """The width or height of the slider, depending on whether it is a horizontal or VERTICAL scrollbar"""
        if self.direction == BGUI_HORIZONTAL_SCROLLBAR:
            return self._slider.size[0]

        elif self.direction == BGUI_VERTICAL_SCROLLBAR:
            return self._slider.size[1]

    @slider_size.setter
    def slider_size(self, size):
        if self.direction == BGUI_HORIZONTAL_SCROLLBAR:
            self._slider.size = [min(1.0, size), 1]

        elif self.direction == BGUI_VERTICAL_SCROLLBAR:
            self._slider.size = [1, min(1.0, size)]

    @property
    def slider_position(self):
        """Sets the x or y coordinate of the slider, depending on whether it is a horizontal or VERTICAL scrollbar"""
        return self._slider.position[self.direction]

    @slider_position.setter
    def slider_position(self, progress):
        self.progress = progress

    def _handle_mouse(self, pos, event):
        super()._handle_mouse(pos, event)

        if event in (BGUI_MOUSE_NONE, BGUI_MOUSE_RELEASE):
            self._slider_offset = None
            self._slider_clicked = False
            self._slot_clicked = False
            return

        # If we're not currently scrolling
        if self._slider_offset is None:

            # If we just started scrolling
            if self._slider_clicked:
                gl_pos = self._slider.gl_position
                dx = gl_pos[0][0] - pos[0]
                dy = gl_pos[0][1] - pos[1]
                self._slider_offset = dx, dy

            # If we can jump
            elif self._slot_clicked:
                click_pos = [pos[0] - self._slider.size[0]/2, pos[1] - self._slider.size[1]/2]
                self._update_slider(click_pos)
                self._slot_clicked = False

        else:
            dx, dy = self._slider_offset
            new_pos = [pos[0] + dx, pos[1] + dy]
            self._update_slider(new_pos, smooth_factor=0.5)

    def _update_slider(self, gl_pos, smooth_factor=0.0):
        current_pos = self._slider._base_pos[:]
        # Untransform gl pos

        # Remove parent position
        gl_pos[self.direction] -= self.position[self.direction]
        gl_pos[self.direction] /= self.size[self.direction]

        slider_size = self._slider._base_size[self.direction]

        max_direction_pos = 1 - slider_size
        new_direction_pos = min(max(gl_pos[self.direction], 0.0), max_direction_pos)
        current_direction_pos = current_pos[self.direction]

        if self._snap_range is not None:
            snap_interval = max_direction_pos / (self._snap_range - 1)
            lerp_direction_pos = round(new_direction_pos / snap_interval) * snap_interval

        else:
            lerp_direction_pos = current_direction_pos + (new_direction_pos - current_direction_pos) * (1 - smooth_factor)

        self.progress = lerp_direction_pos

        if callable(self._on_scroll):
            self._on_scroll(self)