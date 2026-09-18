from machine import Pin
import neopixel
import time

# pin assignments
neopixel_pin = 0
neopixel_power_pin = 2
button_pin = 38 #sw38

# power on neopixel
neopixel_power = Pin(neopixel_power_pin, Pin.OUT) # turn on neopixel
neopixel_power.value(1)

pixel = neopixel.NeoPixel(Pin(neopixel_pin, Pin.OUT), 1)    #pixel is output
button = Pin(button_pin, Pin.IN)    # button is input

def colourON(colour):
    pixel[0] = colour
    pixel.write()

def button_press():

    while True:
        press = button.value()
        time.sleep(0.020)
        release = button.value()
        if press == release:
            return release

def main():

    # colours
    red = (255,0,0)
    green = (0,255,0)
    off = (0,0,0)

    colourON(red)

    num_press = 0
    was_pressed = False

    while True:
        pressed = (button_press() == 0) # active low

        if pressed and not was_pressed:
            num_press += 1
            colourON(green)

        elif (not pressed) and was_pressed:
            if num_press >= 5:
                break

            colourON(red)

        was_pressed = pressed

    colourON(off)
    print('You have successfully implemented LAB1!')


main()
