from pynput import keyboard
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Key, Controller as KeyboardController
import time
import json
import sys
import threading
import keyboard as kb

# Load settings from file
with open("settings_playback.txt", "r") as fopen:
    lines = fopen.readlines()


number_of_plays = int(lines[3][7:].strip(' "\n'))
name_of_recording = lines[0][17:].strip(' "\n')
hotkey = lines[1][23:].strip(' "\n')
hotkey2 = lines[2][23:].strip(' "\n')

supported_keys = [k for k in dir(Key) if not k.startswith('_')]

removed_keys = ['alt','alt_gr', 'alt_l', 'alt_r', 'cmd', 'cmd_r', 'ctrl', 'ctrl_l', 'ctrl-r', 'shift', 'shift_r']

for j in range(len(removed_keys),0):
    supported_keys.remove(removed_keys[j])
            
if hotkey in supported_keys and hotkey2 in supported_keys and hotkey != hotkey2:
    pass
else:
    sys.exit()   

special_keys = {"Key.shift": Key.shift, "Key.tab": Key.tab, "Key.caps_lock": Key.caps_lock, "Key.ctrl": Key.ctrl, "Key.alt": Key.alt, "Key.cmd": Key.cmd, "Key.cmd_r": Key.cmd_r, "Key.alt_r": Key.alt_r, "Key.ctrl_r": Key.ctrl_r, "Key.shift_r": Key.shift_r, "Key.enter": Key.enter, "Key.backspace": Key.backspace, "Key.f19": Key.f19, "Key.f18": Key.f18, "Key.f17": Key.f17, "Key.f16": Key.f16, "Key.f15": Key.f15, "Key.f14": Key.f14, "Key.f13": Key.f13, "Key.media_volume_up": Key.media_volume_up, "Key.media_volume_down": Key.media_volume_down, "Key.media_volume_mute": Key.media_volume_mute, "Key.media_play_pause": Key.media_play_pause, "Key.f6": Key.f6, "Key.f5": Key.f5, "Key.right": Key.right, "Key.down": Key.down, "Key.left": Key.left, "Key.up": Key.up, "Key.page_up": Key.page_up, "Key.page_down": Key.page_down, "Key.home": Key.home, "Key.end": Key.end, "Key.delete": Key.delete, "Key.space": Key.space, "Key.ctrl_l": Key.ctrl_l, "Key.insert": Key.insert, "Key.esc": Key.esc, "Key.f1": Key.f1, "Key.f2": Key.f2, "Key.f3": Key.f3, "Key.f4": Key.f4, "Key.f5": Key.f5, "Key.f6": Key.f6, "Key.f7": Key.f7, "Key.f8": Key.f8, "Key.f9": Key.f9, "Key.f10": Key.f10, "Key.f11": Key.f11, "Key.f12": Key.f12, "Key.print_screen": Key.print_screen, "Key.scroll_lock": Key.scroll_lock, "Key.pause": Key.pause, "Key.alt_l": Key.alt_l, "Key.alt_gr": Key.alt_gr, "Key.menu": Key.menu, "Key.cmd": Key.cmd, "Key.cmd_l": Key.cmd_l, "Key_cmd_r": Key.cmd_r, "Key.ctrl_r": Key.ctrl_r, "Key.down": Key.down, "Key.home": Key.home, "Key.left": Key.left, "Key.media_next": Key.media_next, "Key.media_play_pause": Key.media_play_pause, "Key.media_previous": Key.media_previous, "Key.media_volume_down": Key.media_volume_down, "Key.media_volume_mute": Key.media_volume_mute, "Key.media_volume_up": Key.media_volume_up, "Key.num_lock": Key.num_lock, "Key.right": Key.right, "Key.shift_r": Key.shift_r, "Key.tab": Key.tab, "Key.up": Key.up}

# Load data from recording file
with open(name_of_recording) as json_file:
    data = json.load(json_file)

mouse = MouseController()

# Variables to track recording state
record_all = False

def start_recording():
    global record_all
    record_all = True

def stop_recording():
    global record_all
    record_all = False

kb.add_hotkey(hotkey, start_recording)
kb.add_hotkey(hotkey2, stop_recording)

mouse = MouseController()
keyboard = KeyboardController()

while not record_all:
    time.sleep(0.01)

for loop in range(number_of_plays):
    for index, obj in enumerate(data):
        if not record_all:
            break
        action, _time= obj['action'], obj['_time']
        try:
            next_movement = data[index+1]['_time']
            pause_time = next_movement - _time
        except IndexError as e:
            pause_time = 1

        if action == "pressed_key" or action == "released_key":
            key = obj['key'] if 'Key.' not in obj['key'] else special_keys[obj['key']]
            #print("action: {0}, time: {1}, key: {2}".format(action, _time, str(key)))
            if action == "pressed_key":
                keyboard.press(key)
            else:
                keyboard.release(key)
            time.sleep(pause_time)

        else:
            move_for_scroll = True
            x, y = obj['x'], obj['y']
            if action == "scroll" and index > 0 and (data[index - 1]['action'] == "pressed" or data[index - 1]['action'] == "released"):
                if x == data[index - 1]['x'] and y == data[index - 1]['y']:
                    move_for_scroll = False
                    #print("x: {0}, y: {1}, action: {2}, time: {3}".format(x, y, action, _time))
            mouse.position = (x, y)
            #if action == "pressed" or action == "released" or action == "scroll" and move_for_scroll == True:
            #    time.sleep(0.0)
            if action == "pressed":
                mouse.press(Button.left if obj['button'] == "Button.left" else Button.right)
            elif action == "released":
                mouse.release(Button.left if obj['button'] == "Button.left" else Button.right)
            elif action == "scroll":
                horizontal_direction, vertical_direction = obj['horizontal_direction'], obj['vertical_direction']
                mouse.scroll(horizontal_direction, vertical_direction)
            time.sleep(pause_time)
