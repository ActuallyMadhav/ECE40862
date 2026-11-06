import network
import socket
import time
import esp32
import machine
from machine import Pin

# placeholders need to change
SSID = "YOUR_HOTSPOT_SSID"
PASSWORD = "YOUR_HOTSPOT_PASSWORD"


red_led = Pin(13, Pin.OUT)   # onboard red LED
red_led.value(0)

# Global variables
temp = 0             # measure temperature sensor data
hall = 0             # measure hall sensor data
red_led_state = "OFF"  # string, check state of red led, ON or OFF


def web_page():
    """Function to build the HTML webpage which should be displayed
    in client (web browser on PC or phone) when the client sends a request
    the ESP32 server.

    The server should send necessary header information to the client
    (YOU HAVE TO FIND OUT WHAT HEADER YOUR SERVER NEEDS TO SEND)
    and then only send the HTML webpage to the client.

    Global variables:
    temp, hall, red_led_state
    """

    html_webpage = """<!DOCTYPE HTML><html>
    <head>
    <title>ESP32 Web Server</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.7.2/css/all.css" integrity="sha384-fnmOCqbTlWIlj8LyTjo7mOUStjsKC4pOpQbqyi7RrhN7udi9RwhKkMHpvLbHG9Sr" crossorigin="anonymous">
    <style>
    html {
     font-family: Arial;
     display: inline-block;
     margin: 0px auto;
     text-align: center;
    }
    h1 { font-size: 3.0rem; }
    p { font-size: 3.0rem; }
    .units { font-size: 1.5rem; }
    .sensor-labels{
      font-size: 1.5rem;
      vertical-align:middle;
      padding-bottom: 15px;
    }
    .button {
        display: inline-block; background-color: #e7bd3b; border: none;
        border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none;
        font-size: 30px; margin: 2px; cursor: pointer;
    }
    .button2 {
        background-color: #4286f4;
    }
    </style>
    </head>
    <body>
    <h1>ESP32 WEB Server</h1>
    <p>
    <i class="fas fa-thermometer-half" style="color:#059e8a;"></i>
    <span class="sensor-labels">Temperature</span>
    <span>"""+str(temp)+"""</span>
    <sup class="units">&deg;F</sup>
    </p>
    <p>
    <i class="fas fa-bolt" style="color:#00add6;"></i>
    <span class="sensor-labels">Hall</span>
    <span>"""+str(hall)+"""</span>
    <sup class="units">V</sup>
    </p>
    <p>
    RED LED Current State: <strong>""" + red_led_state + """</strong>
    </p>
    <p>
    <a href="/?red_led=on"><button class="button">RED ON</button></a>
    </p>
    <p>
    <a href="/?red_led=off"><button class="button button2">RED OFF</button></a>
    </p>
    </body>
    </html>"""
    return html_webpage


def connect_wifi():
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


def update_readings():
    global temp, hall, red_led_state
    temp = esp32.raw_temperature()   # degrees F
    hall = esp32.hall_sensor()
    red_led_state = "ON" if red_led.value() else "OFF"


connect_wifi()

# http server socket on port 80
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(addr)
server.listen(5)
print("Web server listening on port 80")

while True:
    conn, client_addr = server.accept()
    try:
        request = conn.recv(1024).decode()
        first_line = request.split("\r\n")[0]
        print("Request from", client_addr[0], ":", first_line)

        # on button press
        if "/?red_led=on" in first_line:
            red_led.value(1)
        elif "/?red_led=off" in first_line:
            red_led.value(0)

        # Measure after changing the LED so the page shows the new state
        update_readings()
        response = web_page()

        # http response headers, blank line, html body
        conn.send("HTTP/1.1 200 OK\r\n")
        conn.send("Content-Type: text/html\r\n")
        conn.send("Connection: close\r\n\r\n")
        conn.sendall(response)
    except Exception as e:
        print("Error handling request:", e)
    finally:
        conn.close()