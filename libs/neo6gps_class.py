from micropyGPS import MicropyGPS
from machine import UART
import time
import math

class Neo6GPS:
    def __init__(self, uart_port=2, uart_baudrate=9600, local_offset=-3, location_formatting='dd'):
        self.uart = UART(uart_port, baudrate=uart_baudrate)
        self.raw_data = ""

        self.my_gps = MicropyGPS(local_offset, location_formatting)

    def __str__(self):
        self.read_raw_data()
        self.update_gps_data()
        return f'Latitude: {self.get_latitude()} Longitude: {self.get_longitude()} Speed [km/h]: {self.get_speed()}\nTimestamp (Epoch 2000): {self.get_timestamp()}\n'

    def read_raw_data(self):
        try:
            self.raw_data = self.uart.read().decode()
        except Exception as e:
            print(f"Failed to read data from GPS: {e}")

    def update_gps_data(self):
        for char in self.raw_data:
            self.my_gps.update(char)

    def get_latitude(self): # [degrees, N/S] convert to decimal degrees
        return self.my_gps.latitude[0] if self.my_gps.latitude[1] == 'N' else -self.my_gps.latitude[0]

    def get_longitude(self): # [degrees, E/W] convert to decimal degrees
        return self.my_gps.longitude[0] if self.my_gps.longitude[1] == 'E' else -self.my_gps.longitude[0]

    def get_speed(self):
        return self.my_gps.speed[2]

    def get_timestamp(self):
        return time.time()    
    
    def get_data(self):
        self.read_raw_data()
        self.update_gps_data()
        return self.get_latitude(), self.get_longitude(), self.get_speed(), self.get_timestamp()
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        # Earth's radius in kilometers (may vary depending on the location)
        radius = 6371 # global avg

        # Convert latitude and longitude to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Calculate differences
        delta_lat = lat2_rad - lat1_rad
        delta_lon = lon2_rad - lon1_rad

        # Haversine formula
        a = math.sin(delta_lat/2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = radius * c

        return distance