from io import StringIO
from texttable import Texttable
from clint import textui
from collections import OrderedDict
from threading import Thread, Event
import time

def draw_box(line, left_conn = False, right_conn = False):
    left = '┤' if left_conn else '│'
    right = '├' if right_conn else '│'
    top = f'┌─{ "─" * len(line) }─┐'
    middle = f'{left} {line} {right}'
    bottom = f'└─{ "─" * len(line) }─┘'
    return top, middle, bottom

def draw_boxes(lines, top_conn = False, bot_conn = False):
    top = '  '
    middle = '  '
    bottom = '  '
    if top_conn:
        top = '│ '
    if bot_conn:
        bottom = '│ '
    if top_conn and bot_conn:
        middle = '├─'
    elif top_conn and not bot_conn:
        middle = '└─'
    elif bot_conn and not top_conn:
        middle = '┌─'
    for i, line in enumerate(lines):
        if i == len(lines) - 1:
            add_top, add_middle, add_bottom = draw_box(line, left_conn=True)
        else:
            add_top, add_middle, add_bottom = draw_box(line, right_conn=True, left_conn=True)
        top += add_top
        middle += add_middle
        bottom += add_bottom
    line = f'{top}\n{middle}\n{bottom}'
    print(line)      

def draw_layers(layers):
    top = None
    bot = None
    for i, layer in enumerate(layers):
        top_conn = False
        bot_conn = False
        if i > 0:
            top_conn = True
        if i < len(layers) - 1:
            bot_conn = True
        draw_boxes(layer, top_conn=top_conn, bot_conn=bot_conn)

def draw_build_tree(layers):
    print('\n'.join(draw_box(' - Build Tree - ')))
    draw_layers([[ m.name for m in layer ] for layer in layers])


class Table:
    def __init__(self, *args):
        self._heading = args
        self._rows = []
    
    def add_row(self, *args):
        for row in args:
            self._rows.append(row)
    
    @property
    def _longest(self):
        return max(map(lambda x: len(x), self._rows))

    def _pad_iter(self, itr, min_len=0, pad=None):
        idx = 0
        for item in itr:
            yield item
            idx += 1
        if idx < min_len:
            for x in range(min_len-idx):
                yield pad

    @property
    def _normalized_rows(self):
        max_len = self._longest
        return [list(self._pad_iter(self._heading, max_len, pad=''))] + [
            list(self._pad_iter(r, max_len, pad='')) for r in self._rows
        ]

    def draw(self):
        table = Texttable()
        table.set_deco(Texttable.HEADER)
        table.set_cols_align(['l' for f in range(self._longest)])
        table.add_rows(self._normalized_rows)
        return table.draw()

class StatusList(Table):
    def __init__(self, name, label):
        super().__init__(name, label)
        self._items = {}

    def add_item(self, name, status):
        self._items[name] = status
    
    def draw(self):
        rows = []
        for name, status in self._items.items():
            mark = ' ✔ ️' if status else ' ✘'
            rows.append([f' - {name}', mark])
        self._rows = rows
        return super().draw()

def draw_modules(modules):
    # table = Texttable()
    # table.set_deco(Texttable.HEADER)
    # table.set_cols_align(['l', 'l'])
    # table.add_rows([['module', 'ok ']] + [[f' - {m.name}', '✔️'] for m in modules])
    # with textui.indent(2):
    #     textui.puts(table.draw())
    table = StatusList('Terraform modules', 'loaded ')
    for m in modules:
        table.add_item(m.name, True  )
    print(table.draw())




class StatusLine(Thread):
    _frames = [
			"🌑 ",
			"🌒 ",
			"🌓 ",
			"🌔 ",
			"🌕 ",
			"🌖 ",
			"🌗 ",
			"🌘 "
		]
    def __init__(self, msg, spinner=True, max_width=80):
        super().__init__()
        self.daemon = True
        self._msg = msg
        self._complete = Event()
        self._exit_status = None
        self._last_len = 0

    def isDone(self):
        return self._complete.is_set()

    def _spinner(self):
        while True:
            for frame in self._frames:
                yield frame

    def _reprint(self, line, **kwargs):
        print(f'\r{" " * self._last_len}', end='')
        print(f'\r{line}', **kwargs)
        self._last_len = len(line)

    def _print_line(self, msg, frame, nl=False):
        self._reprint(f'\r{msg} {frame}', end='\n' if nl else '')

    def _print_exit(self, msg, status, nl=True, **kwargs):
        self._print_line(msg, "✔" if status else "✘", nl=nl, **kwargs)

    def run(self):
        for frame in self._spinner():
            if self._complete.is_set():
                break
            self._print_line(self._msg, frame if self._spinner else '')
            time.sleep(0.2)
        if self._exit_status is not None:
            self._print_exit(self._msg, self._exit_status)
    
    def done(self):
        self._complete.set()

    def success(self):
        self._exit_status = True
        self._complete.set()

    def failure(self):
        self._exit_status = False
        self._complete.set()

    def join(self):
        self.done()
        return super().join()

class StatusList(StatusLine):
    def __init__(self, *args, prefix='-', suffix='...', **kwargs):
        super().__init__(*args, **kwargs)
        self._prefix = prefix
        self._suffix = suffix

    def _print_line(self, msg, frame, nl=False, suffix=True):
        self._reprint(f'\r {self._prefix} {msg}{self._suffix if suffix else ""} {frame}', end='\n' if nl else '')

    def _print_exit(self, *args, **kwargs):
        return super()._print_exit(*args, suffix=False, **kwargs)

    def next(self, success, msg):
        self._print_exit(self._msg, success)
        self._msg = msg

class StatusListContext:
    def __init__(self, header, *args, **kwargs):
        self._header = header
        self._status_line = StatusList(*args, **kwargs)

    def __enter__(self):
        print(f'  {self._header}\n {"-" * (len(self._header) + 2)}')
        self._status_line.start()
        return self._status_line

    def __exit__(self, *args):
        self._status_line.join()

class StatusLineContext:
    def __init__(self, *args, **kwargs):
        self._status_line = StatusLine(*args, **kwargs)

    def __enter__(self):
        self._status_line.start()
        return self._status_line

    def __exit__(self, *args):
        self._status_line.join()