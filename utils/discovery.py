import socket
import requests
import logging
import threading
from onvif import ONVIFCamera
import cv2
from queue import Queue

logging.basicConfig(level=logging.INFO)

# Customize this based on your local subnet
IP_RANGE = "192.168.0.{}"
ONVIF_PORTS = [80, 8000]
RTSP_PORTS = [554, 8554]
TIMEOUT = 1  # seconds
USERNAME = "henriquehesse@me.com"
PASSWORD = "06i19k30e"

COMMON_PATHS = [
    "Streaming/Channels/101",
    "cam/realmonitor?channel=1&subtype=0",
    "h264.sdp",
    "videoMain",
    "live.sdp",
    "ch01.264",
    "media/video1",
    "h264Preview_01_main",
    "stream1",
]

def is_port_open(ip, port):
    try:
        with socket.create_connection((ip, port), timeout=TIMEOUT):
            return True
    except:
        return False

def try_onvif(ip):
    for port in ONVIF_PORTS:
        try:
            cam = ONVIFCamera(ip, port, USERNAME, PASSWORD)
            info = cam.devicemgmt.GetDeviceInformation()
            if "printer" in info.Model.lower() or "hp" in info.Manufacturer.lower():
                return None
            media = cam.create_media_service()
            profile = media.GetProfiles()[0]
            uri = media.GetStreamUri({
                'StreamSetup': {'Stream': 'RTP-Unicast', 'Transport': {'Protocol': 'RTSP'}},
                'ProfileToken': profile.token
            })
            return {
                "ip": ip,
                "port": port,
                "manufacturer": info.Manufacturer,
                "model": info.Model,
                "rtsp": uri.Uri
            }
        except Exception as e:
            continue
    return None

def try_rtsp(ip):
    for port in RTSP_PORTS:
        for path in COMMON_PATHS:
            url = f"rtsp://{USERNAME}:{PASSWORD}@{ip}:{port}/{path}"
            cap = cv2.VideoCapture(url)
            if cap.isOpened():
                ret, _ = cap.read()
                cap.release()
                if ret:
                    return {"ip": ip, "port": port, "rtsp": url}
            cap.release()
    return None

def scan_ip(ip, results):
    if any(is_port_open(ip, p) for p in ONVIF_PORTS + RTSP_PORTS):
        print(f"🔍 Probing {ip}...")
        cam = try_onvif(ip)
        if cam:
            print(f"✅ Found ONVIF Camera at {ip}: {cam['rtsp']}")
            results.put(cam)
            return
        rtsp = try_rtsp(ip)
        if rtsp:
            print(f"✅ Found RTSP Camera at {ip}: {rtsp['rtsp']}")
            results.put(rtsp)

def main():
    threads = []
    results = Queue()
    for i in range(1, 255):
        ip = IP_RANGE.format(i)
        t = threading.Thread(target=scan_ip, args=(ip, results))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("\n🎯 Summary of discovered cameras:")
    while not results.empty():
        cam = results.get()
        print(f" - {cam['ip']}:{cam['port']} → {cam.get('rtsp', 'N/A')}")

if __name__ == "__main__":
    main()