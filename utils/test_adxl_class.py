from adxl345_class import ADXL345
import time
from machine import Pin

def handle_interrupt(pin):
    print("INT MADE")

pin = Pin(4, Pin.IN)
pin.irq(trigger=Pin.IRQ_RISING, handler=handle_interrupt)

# Example usage
accelerometer = ADXL345(sda_pin=21, scl_pin=22)
accelerometer.init()

while True:
    x, y, z = accelerometer.read_accel_data()
    magnitude = accelerometer.calc_accel_magnitude(x, y, z)
    roll = accelerometer.calc_roll(x, y, z)
    pitch = accelerometer.calc_pitch(x, y, z)
    print("X: {:.1f}g, Y: {:.1f}g, Z: {:.1f}g, Magnitude: {:.2f}g, Roll: {:.2f}, Pitch: {:.2f}".format(
        x, y, z, magnitude, roll, pitch))
    time.sleep(0.5)