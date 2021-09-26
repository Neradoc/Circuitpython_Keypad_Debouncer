import supervisor
from micropython import const

STATE = const(0)
ROSE = const(1)
FELL = const(2)
# TIME-2 = const(3)
# TIME-1 = const(4)
TIME = const(5)
HELD = const(6)
HOLD_TIME = const(7)


class HoldTime:
    def __init__(self, deb):
        self.deb = deb

    def __getitem__(self, pos):
        return self.deb.values[pos][HOLD_TIME]

    def __setitem__(self, pos, val):
        self.deb.values[pos][HOLD_TIME] = val

    def set(self, val):
        for pos in range(len(self.deb.values)):
            self.deb.values[pos][HOLD_TIME] = val


class Debouncer:
    def __init__(self, keys, hold_time=1.0):
        self.keypad = keys
        self.timestamp = 0
        self.values = [
            [False, False, False, 0, 0, 0, False, hold_time]
            for _ in range(keys.key_count)
        ]
        self.hold_time = HoldTime(self)

    def update(self):
        for pos in range(len(self.values)):
            self.values[pos][ROSE] = False
            self.values[pos][FELL] = False
        events = []
        while event := self.keypad.events.get():
            events.append(event)
        self.timestamp = supervisor.ticks_ms()
        for event in events:
            pos = event.key_number
            self.values[pos][STATE] = event.pressed
            self.values[pos][ROSE] = event.pressed
            self.values[pos][FELL] = event.released
            self.values[pos][TIME - 2] = self.values[pos][TIME - 1]
            self.values[pos][TIME - 1] = self.values[pos][TIME]
            self.values[pos][TIME] = event.timestamp
            self.values[pos][HELD] = False

    def current_duration(self, pos):
        return self.timestamp - self.values[pos][TIME]

    def last_duration(self, pos):
        return self.timestamp - self.values[pos][TIME - 1]

    def rose(self, pos=None):
        if pos is None:
            return [pp for pp, val in enumerate(self.values) if val[ROSE]]
        else:
            return self.values[pos][ROSE]

    def fell(self, pos=None):
        if pos is None:
            return [pp for pp, val in enumerate(self.values) if val[FELL]]
        else:
            return self.values[pos][FELL]

    def pressed(self, pos=None):
        if pos is None:
            return [pp for pp, val in enumerate(self.values) if val[STATE]]
        else:
            return self.values[pos][STATE]

    def set_hold_times(self, value):
        for pos in range(len(self.values)):
            self.values[pos][HOLD_TIME] = value

    def held(self, pos=None):
        if pos is None:
            return [pp for pp, val in enumerate(self.values) if self.held(pp)]
        if self.values[pos][HELD]:
            return False
        duration = int(self.values[pos][HOLD_TIME] * 1000)
        dt = self.timestamp - self.values[pos][TIME]
        if self.values[pos][STATE] and dt >= duration:
            self.values[pos][HELD] = True
            return True
        return False

    def __repr__(self):
        out = ["{"]
        for pp, val in enumerate(self.values):
            out.append(f"    {pp}: {val}")
        out.append("}")
        return "\n".join(out)
