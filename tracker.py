# Uses adxl345 to wake up the device when it detects movement and read the gps data if more than 10 mins passed since the last reading
from machine import Pin, I2C, deepsleep, lightsleep # active 90~240 mA, active-no-modem (not implemented?) 25~50 mA, lightsleep 0.8 mA, deepsleep 0.15 mA
from adxl345_class import ADXL345
from neo6gps_class import Neo6GPS
import time, struct, esp32, network, urequests
from config import *

def wifi_connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Connecting to network...')
        sta_if.active(True)
        sta_if.connect(WIFI_SSID, WIFI_PWD)
        #while not sta_if.isconnected():
        #    print("Attempting to connect....")
        #    utime.sleep(1)

    if sta_if.isconnected():
        print('Connected! Network config:', sta_if.ifconfig())
        return True
    else:
        print("Failed to connect to network")
        return False

# Setup the ADXL345 accelerometer
accelerometer = ADXL345(sda_pin=21, scl_pin=22)
accelerometer.init()
print("Accelerometer initialized")

# Setup the GPS
gps = Neo6GPS() # might take a few minutes to get accurate data
print("Going to sleep for 2 minutes to search for GPS satellites...")
#deepsleep(120000) # sleep for 2 minutes to get accurate data

# Setup the wake up pin
wake_up_pin = Pin(4, Pin.IN)
esp32.wake_on_ext0(pin=wake_up_pin, level=esp32.WAKEUP_ANY_HIGH)
print("Wake up pin initialized on pin 4")

# Setup the deep sleep time
#ds_time = 10 * 60 * 1000 # 10 minutes
ds_time = 15 * 1000 # 15 seconds
led = Pin (2, Pin.OUT) # Used for knowing when it's awake

while (True):
    print("Reading GPS data")
    gps_data = gps.get_data()
    print(gps.__str__())
    
    distance = gps.calculate_distance(gps_data[0], gps_data[1], HOME_LAT, HOME_LON)
    print("Approximate distance from home:", distance, "km")
    if distance < 0.1:
        print("Close to home, attempting wifi connection")
        if wifi_connect():
            # load data to influxdb using requests, the timestamp should be custom
            print("Attempting to load data to influxdb")
            # It should emulate something like this "insert location,id=Vaca1 lat=-34.707692,lon=-58.270317 1689087600"
            urequests.post("http://influxdb:8086/write?db=tracker", data=f"insert location,id={IDENTIFIER} lat={gps_data[0]},lon={gps_data[1]} {int(time.time())}")
    
    #blink LED
    led.value(1) # AWAKE
    
    time.sleep(3) # ALLOWS STOPPING IN THIS TIME
    #deepsleep(ds_time) # Sleep for 10 minutes or until the accelerometer detects movement
    led.value(0) # SLEEP
    print("Going to sleep for 15 seconds or until accelerometer detects movement")
    time.sleep(0.1) # Needed to print the message
    lightsleep(ds_time) # only turns modem off, cpu paused
    # check if accelerometer woke him up, the 5th bit should be 1
    
    int_data = struct.unpack('B', accelerometer.get_int_source())[0] # b'0xA' before unpacking then 10 after unpacking
    if int_data & 0b00010000:
        print("Woke up from accelerometer")
    else:
        print("Woke up from timer")

