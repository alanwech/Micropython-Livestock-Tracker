# Uses adxl345 to wake up the device when it detects movement and read the gps data if more than 10 mins passed since the last reading
import esp32
from machine import Pin, I2C, deepsleep, lightsleep
from micropyGPS import MicropyGPS
import time
from adxl345_class import ADXL345
from neo6gps_class import GPSData
import time

# Setup the ADXL345 accelerometer
accelerometer = ADXL345(sda_pin=21, scl_pin=22)
accelerometer.init()

# Setup the GPS
uart_port = 2
uart_baudrate = 9600
gps = GPSData(uart_port, uart_baudrate)

# Setup the wake up pin
wake_up_pin = Pin(4, Pin.IN)
esp32.wake_on_ext0(pin=wake_up_pin, level=esp32.WAKEUP_ANY_HIGH)

# Setup the deep sleep time
#ds_time = 10 * 60 * 1000 # 10 minutes
ds_time = 10 * 1000 # 10 seconds
while (True):

    print("Going to sleep for 10 seconds or until accelerometer detects movement")
    deepsleep(ds_time) # Sleep for 10 minutes or until the accelerometer detects movement
    # lightsleep() # only turns modem off, cpu paused
    # check if accelerometer woke him up, the 5th bit should be 1
    if accelerometer.get_int_source() & 0b00010000:
        print("Woke up from accelerometer")
    else:
        print("Woke up from timer")

    print("Reading GPS data")
    print(gps.get_str_data())