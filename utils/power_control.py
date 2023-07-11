from machine import deepsleep, lightsleep, Pin
from time import sleep
import network

led = Pin (2, Pin.OUT)

#blink LED
led.value(1)

# wait 5 seconds so that you can catch the ESP awake to establish a serial communication later
# you should remove this sleep line in your final script
sleep(10)
led.value(0)

print('Im awake, but Im going to sleep')

# deep sleep for 10 seconds, no cpu
deepsleep(10000)

# light sleep for 10 seconds, cpu paused
lightsleep(10000)

# disable modem
ap = network.WLAN(network.AP_IF)
ap.active(False)  # Disable access point
sta_if = network.WLAN(network.STA_IF)
sta_if.active(False)  # Disable station interface