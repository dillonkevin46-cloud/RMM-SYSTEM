import sys
import time
import json
import socket
import platform
import uuid
import psutil
import requests
import mss
import io
import threading
import websocket
import ctypes
import subprocess
import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import os  # <--- Added import

# --- CONFIGURATION ---
SERVER_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws/remote/"
API_CHECKIN = f"{SERVER_URL}/rmm/api/checkin/"
API_TICKET = f"{SERVER_URL}/tickets/api/create/"
AGENT_ID = str(uuid.getnode())

def measure_latency(target="8.8.8.8"):
    try:
        cmd = "ping -n 1 -w 1000" if platform.system() == "Windows" else "ping -c 1 -W 1"
        output = subprocess.check_output(f"{cmd} {target}", shell=True).decode()
        if "time=" in output:
            return int(output.split("time=")[1].split("ms")[0].strip())
        elif "time=" not in output and "ms" in output:
             return int(float(output.split("time=")[1].split(" ")[0]))
    except:
        pass
    return 0

def get_system_info():
    """Collects all hardware specs + performance stats."""
    try:
        mac_num = uuid.getnode()
        mac = ':'.join(('%012X' % mac_num)[i:i+2] for i in range(0, 12, 2))
        ram_gb = f"{round(psutil.virtual_memory().total / (1024.0 **3))} GB"
        hostname = socket.gethostname()
        private_ip = socket.gethostbyname(hostname)

        # Dynamic Stats
        cpu_percent = psutil.cpu_percent(interval=None)
        ram_percent = psutil.virtual_memory().percent
        
        # --- NEW: Disk Usage ---
        # Get usage of the main drive (C:\ on Windows, / on Linux)
        disk_path = 'C:\\' if platform.system() == 'Windows' else '/'
        disk_percent = psutil.disk_usage(disk_path).percent

        latency = measure_latency()

        return {
            "hostname": hostname,
            "agent_id": AGENT_ID,
            "operating_system": f"{platform.system()} {platform.release()}",
            "cpu_model": platform.processor(),
            "ram_total": ram_gb,
            "ram_percent": ram_percent,
            "cpu_percent": cpu_percent,
            "disk_percent": disk_percent, # <--- Sending this to server
            "latency_ms": latency,
            "public_ip": "Checking...",
            "private_ip": private_ip,
            "mac_address": mac,
            "last_login_user": psutil.users()[0].name if psutil.users() else "Unknown"
        }
    except Exception as e:
        print(f"Error gathering info: {e}")
        return {"hostname": socket.gethostname(), "agent_id": AGENT_ID}

# --- GUI TOOLS ---
def native_alert(title, message, style=0):
    try:
        ctypes.windll.user32.MessageBoxW(0, message, title, style | 0x1000)
    except:
        print(f"[{title}] {message}")

def gui_network_test(icon, item):
    def _run_test():
        try:
            requests.get(SERVER_URL, timeout=3)
            native_alert("Network Status", "System is ONLINE ✅", 64)
        except:
            native_alert("Network Status", "System is OFFLINE ❌", 48)
    threading.Thread(target=_run_test).start()

def gui_report_issue(icon, item):
    def _open_input():
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        issue_text = simpledialog.askstring("IT Support", "Describe your issue:", parent=root)
        if issue_text:
            data = {
                "agent_id": AGENT_ID,
                "title": f"Issue Report from {socket.gethostname()}",
                "description": issue_text
            }
            try:
                requests.post(API_TICKET, data=data)
                native_alert("Success", "Ticket sent to IT Support! 🎫", 64)
            except Exception as e:
                native_alert("Error", f"Failed to send ticket: {e}", 16)
        root.destroy()
    threading.Thread(target=_open_input).start()

def exit_action(icon, item):
    icon.stop()
    sys.exit()

def create_image():
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), "black")
    dc = ImageDraw.Draw(image)
    dc.ellipse((16, 16, 48, 48), fill="cyan")
    return image

# --- BACKGROUND TASKS ---
def start_websocket():
    def on_message(ws, message):
        try:
            data = json.loads(message)
            if data.get('type') == 'shell_command':
                cmd = data.get('command')
                print(f">> Executing: {cmd}")
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    output = result.stdout + result.stderr
                    if not output: output = "(Command ran with no output)"
                except Exception as e:
                    output = f"Error executing command: {e}"

                response = {"type": "shell_output", "output": output}
                ws.send(json.dumps(response))
        except Exception as e:
            print(f"WebSocket Message Error: {e}")

    def on_open(ws):
        print(">> WebSocket: Connected (Screen + Terminal)")
        def stream():
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                while ws.sock and ws.sock.connected:
                    try:
                        sct_img = sct.grab(monitor)
                        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                        img = img.resize((1280, 720), Image.Resampling.LANCZOS)
                        buffer = io.BytesIO()
                        img.save(buffer, format="JPEG", quality=50)
                        ws.send(buffer.getvalue(), opcode=websocket.ABNF.OPCODE_BINARY)
                    except:
                        break
                    time.sleep(0.1)
        threading.Thread(target=stream, daemon=True).start()

    while True:
        try:
            ws = websocket.WebSocketApp(f"{WS_URL}{AGENT_ID}/", on_open=on_open, on_message=on_message)
            ws.run_forever()
        except:
            pass
        time.sleep(5)

def start_heartbeat():
    print(f">> Heartbeat: Started for Agent {AGENT_ID}")
    while True:
        try:
            info = get_system_info()
            requests.post(API_CHECKIN, json=info)
        except Exception as e:
            print(f"!! Heartbeat Failed: {e}")
        time.sleep(10)

if __name__ == "__main__":
    print("--------------------------------")
    print(" RMM AGENT STARTING...          ")
    print("--------------------------------")
    threading.Thread(target=start_websocket, daemon=True).start()
    threading.Thread(target=start_heartbeat, daemon=True).start()
    
    print(">> GUI: System Tray Icon Loaded")
    menu = pystray.Menu(
        item('Report Issue', gui_report_issue),
        item('Test Network', gui_network_test),
        item('Exit', exit_action)
    )
    icon = pystray.Icon("RMM Agent", create_image(), "IT Support Agent", menu)
    icon.run()