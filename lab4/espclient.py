import network
import socket
import time
import esp32
import machine
from machine import Timer
 
# placeholders need to change
SSID = "hotspot_name"
PASSWORD = "hotspot_pw"
THINGSPEAK_WRITE_KEY = "write_api_keuy"
THINGSPEAK_HOST = "api.thingspeak.com"

PERIOD_MS = 30000          # timer 30 seconds
RUN_TIME_S = 5 * 60        # run for 5 minutes
 
 
def connect_wifi(): #copied from lab3
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    start = time.ticks_ms()
    while not wlan.isconnected():
        if time.ticks_diff(time.ticks_ms(), start) > 20000:  # 20s time for esp to connect otherwise throw error
            raise RuntimeError("Wi-Fi connection timed out")
        machine.idle()
    print("Connected to", wlan.config("essid"))
    print("IP Address:", wlan.ifconfig()[0])
    return wlan
 
 
def send_to_thingspeak(temp, hall):
    #Send one temperature+hall reading to web using http get
    path = "/update?api_key={}&field1={}&field2={}".format(
        THINGSPEAK_WRITE_KEY, temp, hall)
    request = ("GET {} HTTP/1.1\r\n"
               "Host: {}\r\n"
               "Connection: close\r\n\r\n").format(path, THINGSPEAK_HOST)
 
    addr = socket.getaddrinfo(THINGSPEAK_HOST, 80)[0][-1]
    s = socket.socket()
    try:
        s.connect(addr)
        s.send(request.encode())
        response = s.recv(512)
        status = response.split(b"\r\n")[0].decode()
        print("ThingSpeak response:", status)
    finally:
        s.close()
 
 
def timer_callback(t):
    # measure then print then upload every 30s
    temp = esp32.raw_temperature()   # degrees F
    hall = esp32.hall_sensor()
    print("Temperature: {} F   Hall: {}".format(temp, hall))
    try:
        send_to_thingspeak(temp, hall)
    except Exception as e:
        print("Upload failed:", e)
 
 
connect_wifi()
 
timer = Timer(0)
timer.init(period=PERIOD_MS, mode=Timer.PERIODIC, callback=timer_callback)
 
# Let the timer fire 10 times w 30s intervals - 30, 60, ..., 300 then stop
time.sleep(RUN_TIME_S + 5)
timer.deinit()
print("ran for 5 minutes.")