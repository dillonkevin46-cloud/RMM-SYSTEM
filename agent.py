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

# --- CONFIGURATION ---
SERVER_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws/remote/"
API_CHECKIN = f"{SERVER_URL}/rmm/api/checkin/"
API_TICKET = f"{SERVER_URL}/tickets/api/create/"
AGENT_ID = str(uuid.getnode())

# --- HELPER: Measure Ping ---
def measure_latency(target="8.8.8.8"):
    """Pings a server to measure latency in ms."""
    try:
        # Windows ping command: -n 1 (count), -w 1000 (timeout)
        output = subprocess.check_output(f"ping -n 1 -w 1000 {target}", shell=True).decode()
        if "time=" in output:
            return int(output.split("time=")[1].split("ms")[0])
    except:
        pass
    return 0

# --- HELPER: Gather System Info ---
def get_system_info():
    """Collects all hardware specs + performance stats."""
    try:
        # Static Info
        mac_num = uuid.getnode()
        mac = ':'.join(('%012X' % mac_num)[i:i+2] for i in range(0, 12, 2))
        ram_gb = f"{round(psutil.virtual_memory().total / (1024.0 **3))} GB"
        hostname = socket.gethostname()
        private_ip = socket.gethostbyname(hostname)

        # Dynamic Stats (For Graphs)
        cpu_percent = psutil.cpu_percent(interval=1)
        ram_percent = psutil.virtual_memory().percent
        latency = measure_latency()

        return {
            "hostname": hostname,
            "agent_id": AGENT_ID,
            "operating_system": f"{platform.system()} {platform.release()}",
            "cpu_model": platform.processor(),
            "ram_total": ram_gb,
            "ram_percent": ram_percent,   # Graph Data
            "cpu_percent": cpu_percent,   # Graph Data
            "latency_ms": latency,        # Graph Data
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
    """Styles: 0=OK, 48=Warning, 64=Info. Block: 0x1000 = System Modal"""
    ctypes.windll.user32.MessageBoxW(0, message, title, style | 0x1000)

def gui_network_test(icon, item):
    """Checks internet connection without freezing the app."""
    def _run_test():
        try:
            requests.get(SERVER_URL, timeout=3)
            native_alert("Network Status", "System is ONLINE ✅", 64)
        except:
            native_alert("Network Status", "System is OFFLINE ❌", 48)
    threading.Thread(target=_run_test).start()

def gui_report_issue(icon, item):
    """Opens ticket popup without freezing the app."""
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
    """Runs Remote Desktop Streaming."""
    def on_open(ws):
        print(">> WebSocket: Connected to Screen Stream")
        def stream():
            with mss.mss() as sct:
                monitor = sct.monitors[1]
                while ws.sock and ws.sock.connected:
                    sct_img = sct.grab(monitor)
                    img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                    img = img.resize((1280, 720), Image.Resampling.LANCZOS)
                    buffer = io.BytesIO()
                    img.save(buffer, format="JPEG", quality=50)
                    try:
                        ws.send(buffer.getvalue(), opcode=websocket.ABNF.OPCODE_BINARY)
                    except:
                        break
                    time.sleep(0.05)
        threading.Thread(target=stream, daemon=True).start()

    while True:
        try:
            ws = websocket.WebSocketApp(f"{WS_URL}{AGENT_ID}/", on_open=on_open)
            ws.run_forever()
        except:
            pass
        time.sleep(5)

def start_heartbeat():
    """Runs 10s check-in loop."""
    print(f">> Heartbeat: Started for Agent {AGENT_ID}")
    while True:
        try:
            info = get_system_info()
            r = requests.post(API_CHECKIN, json=info)
            if r.status_code != 200:
                print(f"!! Heartbeat Error: Server said {r.status_code}")
        except Exception as e:
            print(f"!! Heartbeat Failed: {e}")
        time.sleep(10)

# --- MAIN ENTRY POINT ---
if __name__ == "__main__":
    print("--------------------------------")
    print(" RMM AGENT STARTING...          ")
    print("--------------------------------")

    # Start Background Threads
    threading.Thread(target=start_websocket, daemon=True).start()
    threading.Thread(target=start_heartbeat, daemon=True).start()
    
    print(">> GUI: System Tray Icon Loaded")
    
    # Start Icon
    menu = pystray.Menu(
        item('Report Issue', gui_report_issue),
        item('Test Network', gui_network_test),
        item('Exit', exit_action)
    )
    
    icon = pystray.Icon("RMM Agent", create_image(), "IT Support Agent", menu)
    icon.run()