from micropyGPS import MicropyGPS
from machine import UART
import time

class GPSData:
    def __init__(self, uart_port, uart_baudrate):
        self.uart = UART(uart_port, baudrate=uart_baudrate)
        self.raw_data = ""

        self.my_gps = MicropyGPS(local_offset=-3, location_formatting='dd')

    def read_raw_data(self):
        self.raw_data = self.uart.read().decode()

    def update_gps_data(self):
        for char in self.raw_data:
            self.my_gps.update(char)

    def get_latitude(self):
        return self.my_gps.latitude

    def get_longitude(self):
        return self.my_gps.longitude

    def get_speed(self):
        return self.my_gps.speed[2]

    def get_timestamp(self):
        return time.time()
    
    def get_str_data(self):
        self.read_raw_data()
        self.update_gps_data()
        return f'Latitude: {self.get_latitude()}\nLongitude: {self.get_longitude()}\nSpeed [km/h]: {self.get_speed()}\nTimestamp (Epoch 2000): {self.get_timestamp()}'