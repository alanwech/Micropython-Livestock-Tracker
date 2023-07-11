from neo6gps_class import GPSData
import time

uart_port = 2
uart_baudrate = 9600

gps = GPSData(uart_port, uart_baudrate)

while True:
    gps.read_raw_data()
    gps.update_gps_data()

    latitude = gps.get_latitude()
    longitude = gps.get_longitude()
    speed = gps.get_speed()
    timestamp = gps.get_timestamp()

    print(f'Latitude: {latitude}\nLongitude: {longitude}\nSpeed [km/h]: {speed}\nTimestamp (Epoch 2000): {timestamp}')

    time.sleep(1)