import supervisor
from micropython import const

_STATE = const(0)
_ROSE = const(1)
_FELL = const(2)
# _TIME-2 = const(3)
# _TIME-1 = const(4)
_TIME = const(5)
_HELD = const(6)
_HOLD_TIME = const(7)


class HoldTime:
    def __init__(self, deb):
        self.deb = deb

    def __getitem__(self, pos):
        return self.deb.values[pos][_HOLD_TIME]

    def __setitem__(self, pos, val):
        self.deb.values[pos][_HOLD_TIME] = val

    def set(self, val):
        for pos in range(len(self.deb.values)):
            self.deb.values[pos][_HOLD_TIME] = val


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
            self.values[pos][_ROSE] = False
            self.values[pos][_FELL] = False
        events = []
        while event := self.keypad.events.get():
            events.append(event)
        self.timestamp = supervisor.ticks_ms()
        for event in events:
            pos = event.key_number
            self.values[pos][_STATE] = event.pressed
            self.values[pos][_ROSE] = event.pressed
            self.values[pos][_FELL] = event.released
            self.values[pos][_TIME - 2] = self.values[pos][_TIME - 1]
            self.values[pos][_TIME - 1] = self.values[pos][_TIME]
            self.values[pos][_TIME] = event.timestamp
            self.values[pos][_HELD] = False

    def current_duration(self, pos):
        return (self.timestamp - self.values[pos][_TIME]) / 1000

    def last_duration(self, pos):
        return (self.timestamp - self.values[pos][_TIME - 1]) / 1000

    def rose(self, pos=None):
        if pos is None:
            return [pp for pp, val in enumerate(self.values) if val[_ROSE]]
        else:
            return self.values[pos][_ROSE]

    def fell(self, pos=None):
        if pos is None:
            return [pp for pp, val in enumerate(self.values) if val[_FELL]]
        else:
            return self.values[pos][_FELL]

    def pressed(self, pos=None):
        if pos is None:
            return [pp for pp, val in enumerate(self.values) if val[_STATE]]
        else:
            return self.values[pos][_STATE]

    def set_hold_times(self, value):
        for pos in range(len(self.values)):
            self.values[pos][_HOLD_TIME] = value

    def held(self, pos=None):
        if pos is None:
            return [pp for pp, val in enumerate(self.values) if self.held(pp)]
        if self.values[pos][_HELD]:
            return False
        duration = int(self.values[pos][_HOLD_TIME] * 1000)
        dt = self.timestamp - self.values[pos][_TIME]
        if self.values[pos][_STATE] and dt >= duration:
            self.values[pos][_HELD] = True
            return True
        return False

    def __repr__(self):
        out = ["{"]
        for pp, val in enumerate(self.values):
            out.append(f"    {pp}: {val}")
        out.append("}")
        return "\n".join(out)
