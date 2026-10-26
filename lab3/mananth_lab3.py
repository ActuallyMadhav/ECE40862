import network
import ntptime
import time
import esp32
import machine
from machine import Pin, Timer, RTC, TouchPad
from neopixel import NeoPixel

SSID = "hotspot_name" #placeholder change to actual name
PASSWORD = "hotspot_password" #placeholder

TOUCH_THRESHOLD = None

RED_LED_PIN = 13
NEOPIXEL_PIN = 0
NEOPIXEL_POWER_PIN = 2  
TOUCH_PIN = 14
BUTTON_PIN = 32          

GREEN = (0, 255, 0)
OFF = (0, 0, 0)

AWAKE_MS = 30000
SLEEP_MS = 60000
DISPLAY_MS = 15000
TOUCH_MS = 50

red_led = Pin(RED_LED_PIN, Pin.OUT)
red_led.value(1)

np_power = Pin(NEOPIXEL_POWER_PIN, Pin.OUT)
np_power.value(1)
np = NeoPixel(Pin(NEOPIXEL_PIN, Pin.OUT), 1)
np[0] = OFF
np.write()

touch = TouchPad(Pin(TOUCH_PIN))
button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_DOWN)
rtc = RTC()

if machine.reset_cause() == machine.DEEPSLEEP_RESET:
    reason = machine.wake_reason()
    if reason == machine.EXT0_WAKE:
        print("Woke up due to EXT0 wakeup.")
    elif reason == machine.TIMER_WAKE:
        print("Woke up due to Timer wakeup.")
    else:
        print("Woke up due to unknown source:", reason)


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


def nth_sunday(year, month, n):
    first = time.mktime((year, month, 1, 0, 0, 0, 0, 0))
    weekday = time.localtime(first)[6]  # mon = 0, sun = 6
    return 1 + (6 - weekday) % 7 + 7 * (n - 1)


def is_us_dst(utc_secs):
    year = time.localtime(utc_secs)[0]
    start = time.mktime((year, 3, nth_sunday(year, 3, 2), 7, 0, 0, 0, 0))
    end = time.mktime((year, 11, nth_sunday(year, 11, 1), 6, 0, 0, 0, 0))
    return start <= utc_secs < end


def sync_time():
    ntptime.host = "pool.ntp.org"
    for _ in range(5):
        try:
            ntptime.settime()  # change rtc to utc
            break
        except OSError:
            pass
    else:
        raise RuntimeError("NTP sync failed")

    utc = time.time()
    offset_hours = -4 if is_us_dst(utc) else -5  # edt or est
    local = time.localtime(utc + offset_hours * 3600)
    rtc.datetime((local[0], local[1], local[2], local[6],
                  local[3], local[4], local[5], 0))


def show_datetime(timer):
    year, month, day, _, hour, minute, second, _ = rtc.datetime()
    print("Date: {:02d}/{:02d}/{:04d}".format(month, day, year))
    print("Time: {:02d}:{:02d}:{:02d} HRS".format(hour, minute, second))


def calibrate_touch(samples=20):
    total = 0
    for _ in range(samples):
        total += touch.read()
    baseline = total // samples

    threshold = int(baseline * 0.7)
    print("Touch baseline:", baseline, "threshold:", threshold)
    return threshold


touch_on = False


def check_touch(timer):
    global touch_on
    try:
        value = touch.read()
    except ValueError:
        return
    touched = value < threshold
    if touched != touch_on:
        touch_on = touched
        np[0] = GREEN if touched else OFF
        np.write()


def go_to_sleep(timer):
    print("I am going to sleep for 1 minute.")
    display_timer.deinit()
    touch_timer.deinit()
    sleep_timer.deinit()
    np[0] = OFF
    np.write()
    np_power.value(0)
    red_led.value(0)
    esp32.wake_on_ext0(pin=button, level=esp32.WAKEUP_ANY_HIGH)
    machine.deepsleep(SLEEP_MS)


connect_wifi()
sync_time()

threshold = TOUCH_THRESHOLD if TOUCH_THRESHOLD is not None else calibrate_touch()

# Display timer starts first so its 30s print before sleep timer start
display_timer = Timer(0)
display_timer.init(period=DISPLAY_MS, mode=Timer.PERIODIC, callback=show_datetime)

touch_timer = Timer(1)
touch_timer.init(period=TOUCH_MS, mode=Timer.PERIODIC, callback=check_touch)

sleep_timer = Timer(2)
sleep_timer.init(period=AWAKE_MS, mode=Timer.ONE_SHOT, callback=go_to_sleep)