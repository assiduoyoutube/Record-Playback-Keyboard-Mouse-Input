from pynput import mouse
from pynput import keyboard
from pynput.keyboard import Key

import time
import json
import sys
import keyboard as kb

fopen = open("settings_record.txt","r")
fread = fopen.readlines()

name_of_recording = fread[0][17:].split()[0][1:-1]
hotkey = fread[1][24:].split()[0][1:-1]
hotkey2 = fread[2][23:].split()[0][1:-1]

supported_keys = [k for k in dir(Key) if not k.startswith('_')]

removed_keys = ['alt','alt_gr', 'alt_l', 'alt_r', 'cmd', 'cmd_r', 'ctrl', 'ctrl_l', 'ctrl-r', 'shift', 'shift_r']

for j in range(len(removed_keys),0):
    supported_keys.remove(removed_keys[j])
            
if hotkey in supported_keys and hotkey2 in supported_keys and hotkey != hotkey2:
    pass
else:
    sys.exit()    

record_all = False
recording_started = False
exit_program = False

storage = []
count = 0

start_stop_recording = False

def startrecording():
    global start_stop_recording
    start_stop_recording = True

def stoprecording():
    global start_stop_recording
    start_stop_recording = False 

kb.add_hotkey(hotkey, startrecording)
kb.add_hotkey(hotkey2, stoprecording)

def start_recording():
    global record_all
    record_all = True

def stop_recording():
    global record_all
    global exit_program
    global recording_started
    record_all = False

    altered_storage = []
    for i in range(len(storage)):
        if (storage[i]["action"] == "released_key" or storage[i]["action"] == "pressed key"):
            if storage[i]["key"] != "Key.%s" % (hotkey) or storage[i]["key"] != "Key.%s" % (hotkey2):
                altered_storage.append(storage[i])
            elif storage[i]["key"] == "Key.%s" % (hotkey) or storage[i]["key"] == "Key.%s" % (hotkey2):
                pass
        else:
            altered_storage.append(storage[i])

    altered_storage = altered_storage[1:]
            
    with open('{}'.format(name_of_recording), 'w') as outfile:
        json.dump(altered_storage, outfile)
    mouse_listener.stop()
    recording_started = False
    exit_program = True
    sys.exit()

pressed_keys = set() 

def on_press(key):
    global recording_started
    global start_stop_recording

    if start_stop_recording == True:
        start_recording()
        recording_started = True
    else:
        stop_recording()
        recording_started = False

    if recording_started:
        if key not in pressed_keys:
            pressed_keys.add(key)
            try:
                json_object = {'action': 'pressed_key', 'key': key.char, '_time': time.time()}
            except AttributeError:
                json_object = {'action': 'pressed_key', 'key': str(key), '_time': time.time()}
            storage.append(json_object)

def on_release(key):
    global start_stop_recording

    if start_stop_recording == True:
        start_recording()
        recording_started = True
    else:
        stop_recording()
        recording_started = False

    if recording_started:
        if key in pressed_keys:
            try:
                json_object = {'action': 'released_key', 'key': key.char, '_time': time.time()}
            except AttributeError:
                json_object = {'action': 'released_key', 'key': str(key), '_time': time.time()}
            storage.append(json_object)
            pressed_keys.remove(key)

def on_move(x, y):
    global start_stop_recording
    if start_stop_recording == True:
        start_recording()
        recording_started = True
    else:
        stop_recording()
        recording_started = False


    if record_all and recording_started:
        json_object = {'action': 'moved', 'x': x, 'y': y, '_time': time.time()}
        storage.append(json_object)

def on_click(x, y, button, pressed):
    global start_stop_recording
    if start_stop_recording == True:
        start_recording()
        recording_started = True
    else:
        stop_recording()
        recording_started = False


    if recording_started:
        json_object = {'action': 'pressed' if pressed else 'released', 'button': str(button), 'x': x, 'y': y, '_time': time.time()}
        storage.append(json_object)

def on_scroll(x, y, dx, dy):
    global start_stop_recording
    if start_stop_recording == True:
        start_recording()
        recording_started = True
    else:
        stop_recording()
        recording_started = False

    if recording_started:
        json_object = {'action': 'scroll', 'vertical_direction': int(dy), 'horizontal_direction': int(dx), 'x': x, 'y': y, '_time': time.time()}
        storage.append(json_object)

keyboard_listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)

while not start_stop_recording:
    time.sleep(0.1)

mouse_listener = mouse.Listener(
    on_click=on_click,
    on_scroll=on_scroll,
    on_move=on_move)

keyboard_listener.start()
mouse_listener.start()
keyboard_listener.join()
mouse_listener.join()

while not exit_program:
    time.sleep(0)