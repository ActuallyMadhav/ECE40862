from machine import Pin, ADC, PWM, RTC, Timer
import machine

BUTTON_PIN = 38
POT_PIN = 34
LED_PIN = 14

DISPLAY_PERIOD_MS = 30000
ADC_PERIOD_MS = 100
DEBOUNCE_MS = 50

INIT_FREQ = 10          # Hz
INIT_DUTY = 512         # 50% 
FREQ_MIN = 1            # Hz, pot fully one way
FREQ_MAX = 60           # Hz, pot fully the other way
ADC_MAX = 4095          # 12-bit reading
FREQ_HYSTERESIS = 40    # raw ADC count

# Control modes
MODE_NONE = 0           
MODE_FREQ = 1           # pot controls PWM frequency
MODE_DUTY = 2           # pot controls PWM duty cycle

WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday",
            "Friday", "Saturday", "Sunday")

mode = MODE_NONE
debounce_active = False
last_freq_raw = None

def ask_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Please enter a whole number.")


year = ask_int("Year? ")
month = ask_int("Month? ")
day = ask_int("Day? ")
weekday = ask_int("Weekday? ")          # 0 = Monday ... 6 = Sunday
hour = ask_int("Hour? ")
minute = ask_int("Minute? ")
second = ask_int("Second? ")
microsecond = ask_int("Microsecond? ")

rtc = RTC()
rtc.datetime((year, month, day, weekday, hour, minute, second, microsecond))


button = Pin(BUTTON_PIN, Pin.IN)        # GPIO 38 

pot = ADC(Pin(POT_PIN))
pot.atten(ADC.ATTN_11DB)               

led_pwm = PWM(Pin(LED_PIN), freq=INIT_FREQ, duty=INIT_DUTY)

display_timer = Timer(0)
adc_timer = Timer(1)
debounce_timer = Timer(2)

def read_pot():
    """Return the pot reading scaled to 0-4095."""
    return pot.read_u16() >> 4

def pot_to_freq(raw):
    return FREQ_MIN + (raw * (FREQ_MAX - FREQ_MIN)) // ADC_MAX


def pot_to_duty(raw):
    return raw >> 2   


def print_datetime():
    y, mo, d, wd, h, mi, s, _ = rtc.datetime()
    print("Date: {:02d}/{:02d}/{:04d} ({})".format(mo, d, y, WEEKDAYS[wd]))
    print("Time: {:02d}:{:02d}:{:02d} EDT".format(h, mi, s))


def display_cb(t):
    print_datetime()


def adc_cb(t):
    global last_freq_raw
    raw = read_pot()

    if mode == MODE_FREQ:
        if last_freq_raw is None or abs(raw - last_freq_raw) > FREQ_HYSTERESIS:
            last_freq_raw = raw
            led_pwm.freq(pot_to_freq(raw))
    elif mode == MODE_DUTY:
        led_pwm.duty(pot_to_duty(raw))


def debounce_cb(t):
    global mode, debounce_active, last_freq_raw
    if button.value() == 0:             # still held down means real press
        if mode == MODE_FREQ:
            mode = MODE_DUTY
            print("Switch pressed: pot now controls DUTY CYCLE")
        else:                           # first press
            mode = MODE_FREQ
            last_freq_raw = None        
            print("Switch pressed: pot now controls FREQUENCY")
    debounce_active = False


def button_cb(pin):
    global debounce_active
    if not debounce_active:
        debounce_active = True
        debounce_timer.init(mode=Timer.ONE_SHOT, period=DEBOUNCE_MS,
                            callback=debounce_cb)


print_datetime()
display_timer.init(mode=Timer.PERIODIC, period=DISPLAY_PERIOD_MS, callback=display_cb)
adc_timer.init(mode=Timer.PERIODIC, period=ADC_PERIOD_MS, callback=adc_cb)
button.irq(trigger=Pin.IRQ_FALLING, handler=button_cb)

try:
    while True:
        machine.idle()                  
except KeyboardInterrupt:
    display_timer.deinit()
    adc_timer.deinit()
    debounce_timer.deinit()
    button.irq(handler=None)
    led_pwm.deinit()
    print("Stopped.")
