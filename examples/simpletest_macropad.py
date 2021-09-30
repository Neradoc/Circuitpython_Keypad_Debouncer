import board
import keypad
import time

from keypad_debouncer import Debouncer

KEY_PINS = (board.KEY1, board.KEY2, board.KEY3, board.KEY4, board.KEY5, board.KEY6, board.KEY7, board.KEY8, board.KEY9, board.KEY10, board.KEY11, board.KEY12)
keypad_keys = keypad.Keys(KEY_PINS, value_when_pressed=False, pull=True)

db = Debouncer(keypad_keys, hold_time=4.0)

while True:
    # snapshot the button state for this "frame"
    db.update()
    
    # test rose of one button
    if db.rose(0):
        print("Pressed Key 0")
    # test fell of one button
    if db.fell(0):
        print(f"Held Key 0 for {db.last_duration(0):f}s")

    # test if a button was held a certain amount of time (triggers once, like rose)
    if db.held(0):
        dur = db.current_duration(0)
        print(f"Holding long Key 0 ({dur:f})")

    # get the list of all buttons that rose in last frame
    roses = db.rose()
    if len(roses):
        print("roses", repr(roses))

    # get the list of all buttons that became held above the time during last frame
    held = db.held()
    if len(held):
        print("helds", [
            (pos, db.current_duration(pos) / 1000)
            for pos in held
        ])

    db.hold_time[4] = 5.0
