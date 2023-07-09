from micropyGPS import MicropyGPS
from machine import UART
import time

# Setup UART
uart = UART(2, baudrate=9600) # can use UART 1-2 TX2/RX2, UART0 is used for live console
raw_gps = uart.read().decode()
#raw_gps = '$GPRMC,081836,A,3751.65,S,14507.36,E,000.0,360.0,130998,011.3,E*62'

# Setup GPS Parser
my_gps = MicropyGPS(local_offset=-3, location_formatting='dd') # UTC -3, Use decimal coordinates instead of hour/mins

for x in raw_gps:
    my_gps.update(x)

# Process information
lat = my_gps.latitude
long = my_gps.longitude
speed = my_gps.speed[2] # km/h
# The GPS library already updates date and time in the ESP32 using the time library
#ts = my_gps.timestamp # hh/mm/ss
#dt = my_gps.date_string('s_dmy') # dd/mm/yy

ts = time.time()

print(f'Latitude: {lat}\nLongitude: {long}\nSpeed [km/h]: {speed}\nTimestamp (Epoch 2000): {ts}')