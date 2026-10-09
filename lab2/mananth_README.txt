External LED (PWM output):
  ESP32 GPIO 14 -> 220 ohm resistor -> LED Anode (+, longer leg)
  LED Cathode (-, shorter leg) -> ESP32 GND
 
Potentiometer (analog input, ADC1):
  Pot outer pin 1 -> ESP32 3V
  Pot outer pin 2 -> ESP32 GND
  Pot middle pin (wiper) -> ESP32 GPIO 34 (A2, ADC1_CH6)
 
Switch (digital input):
  On-board user button -> ESP32 GPIO 38 (already wired on the board, active LOW; no external connection needed)
 
Timers used:
  Timer 0 - prints RTC date and time every 30 s
  Timer 1 - reads the potentiometer every 100 ms
  Timer 2 - one-shot 50 ms switch debounce

youtube video:
https://youtu.be/hpjGAyQ1mGI