import board
import keypad
import time

from keypad_debouncer import Debouncer

KEY_PINS = (board.KEY1, board.KEY2, board.KEY3, board.KEY4, board.KEY5, board.KEY6, board.KEY7, board.KEY8, board.KEY9, board.KEY10, board.KEY11, board.KEY12)
keypad_keys = keypad.Keys(KEY_PINS, value_when_pressed=False, pull=True)

db = Debouncer(keypad_keys, hold_time=4.0)

while True:
    db.update()
    if db.rose(0):
        print("Pressed Key 0")
    if db.fell(0):
        print(f"Held Key 0 for {db.last_duration(0) / 1000}s")
    if db.held(0):
        print("Holding long Key 0")

    roses = db.rose()
    if len(roses):
        print("roses", repr(roses))

    held = db.held()
    if len(held):
        print("helds", repr(held))

    db.hold_time[4] = 5.0
