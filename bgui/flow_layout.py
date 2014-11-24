from .frame import Frame
from .widget import BGUI_DEFAULT, BGUI_FLOW_COLUMN, BGUI_FLOW_ROW

from contextlib import contextmanager
from inspect import signature

BGUI_FLOW_ROW = 0
BGUI_FLOW_COLUMN = 1


class FlowLayout(Frame):
    """Layout class with row() and column() support"""

    theme_section = 'FlowLayout'

    def __init__(self, parent, name=None, border=None, aspect=None, size=None, pos=None, sub_theme='',
                 options=BGUI_DEFAULT, flow_type=BGUI_FLOW_COLUMN):
        self._insert_at = [0.0, 1.0]
        self._flow_type = flow_type

        if pos is None:
            pos = [0.0, 0.0]
        else:
            pos = pos[:]

        if size is None:
            size = [1.0, 1.0]

        else:
            size = size[:]

        super().__init__(parent, name, border, aspect, size, pos, sub_theme, options, clip)

    @contextmanager
    def _insert_element(self, size, alternate_size=1.0, padding=0.0):
        index = self._flow_type

        if index == BGUI_FLOW_ROW:
            direction_switch = 1

        else:
            direction_switch = -1

        insert_size = [alternate_size, alternate_size]
        padded_size = max(size - (2 * padding), 0.0)
        insert_size[self._flow_type] = padded_size

        delta_size = size - padded_size
        adjusted_padding = delta_size / 2

        self._insert_at[self._flow_type] += direction_switch * adjusted_padding

        # Account for the fact we work downwards. Columns will make this permanent with the next insert position
        insert_at = self._insert_at[:]
        insert_at[BGUI_FLOW_COLUMN] -= insert_size[BGUI_FLOW_COLUMN]

        yield insert_size[:], insert_at

        self._insert_at[self._flow_type] += direction_switch * (adjusted_padding + insert_size[index])

    def column(self, size, *, alternate_size=1.0, padding=0.0, **kwargs):
        """Create a child column and follow internal direction information
        :param width: width of row
        :param height: height of row
        :param name: name of added row
        """
        with self._insert_element(size, alternate_size, padding) as (size, pos):
            column = UILayout(self, size=size, pos=pos, flow_type=BGUI_FLOW_COLUMN, **kwargs)

        return column

    def row(self, size, *, alternate_size=1.0, padding=0.0, **kwargs):
        """Create a child row and follow internal direction information
        :param height: height of row
        :param width: width of row
        :param name: name of added row
        """
        with self._insert_element(size, alternate_size, padding) as (size, pos):
            row = UILayout(self, size=size, pos=pos, flow_type=BGUI_FLOW_ROW, **kwargs)

        return row

    def separator(self, size=0.0):
        with self._insert_element(size):
            pass

    def widget(self, widget_cls, *, size=1.0, alternate_size=1.0, **kwargs):
        """Create a child widget and follow internal direction information
        :param widget_cls: widget class
        :param size: size of widget in layout direction
        :param name: name of added widget
        """
        if 'size' in signature(widget_cls).parameters:

            if self._flow_type == BGUI_FLOW_ROW:
                ordered_size = [size, alternate_size]

            else:
                ordered_size = [alternate_size, size]

            kwargs['size'] = ordered_size

        widget = widget_cls(self, **kwargs)

        # Take into account widgets using aspect option (or without size argument)
        if self._flow_type == BGUI_FLOW_ROW:
            size, alternate_size = widget._base_size

        else:
            alternate_size, size = widget._base_size

        with self._insert_element(size, alternate_size, 0.0) as (size_, pos):
            widget._update_position(None, pos)

        return widget
