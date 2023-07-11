from machine import Pin, I2C
import time
import ustruct
import math
import micropython

micropython.alloc_emergency_exception_buf(100)  # Necessary for raising exceptions during interruptions


class ADXL345:
    def __init__(self, sda_pin=21, scl_pin=22, freq=100000):
        self.accelerometer_id = 0x53

        self.power_ctl = 0x2D
        self.data_format = 0x31
        self.bw_rate = 0x2C
        self.data_x0 = 0x32
        self.thresh_act = 0x24
        self.int_enable = 0x2E
        self.int_source = 0x30
        self.act_inact_ctl = 0x27

        self.i2c = I2C(sda=Pin(sda_pin), scl=Pin(scl_pin), freq=freq) # Can use SoftI2C alternatively

    def write_register(self, address, data): # register address as hex, data as bytearray
        self.i2c.writeto_mem(self.accelerometer_id, address, data)

    def read_register(self, address, nbytes): # register address as hex, nbytes as int
        return self.i2c.readfrom_mem(self.accelerometer_id, address, nbytes)

    # Initialize ADXL345, 4mg/LSB -> x = 245~0.98g
    def init(self):
        self.write_register(self.data_format, bytearray([0x09]))  # Full resolution; 0x09 for +-4g; 0x0B for +/- 16g
        self.write_register(self.power_ctl, bytearray([0x08]))  # Set bit 3 to 1 to enable measurement mode
        self.write_register(self.bw_rate, bytearray([0x18]))  # Set low power mode and ODR to 25Hz
        self.write_register(self.thresh_act, bytearray([0x07]))  # 62.5 mg/LSB -> triggers at 0.4375g
        self.write_register(self.int_enable, bytearray([0x10]))  # Enable Activity interruption
        self.write_register(self.act_inact_ctl, bytearray([0xE0]))  # Activity ac mode, enable only XY axis for detection

    def get_int_source(self):
        return self.read_register(self.int_source, 1) # Clears interruption flags
    
    def get_accel_data(self, raw=False):
        data = self.read_register(self.data_x0, 6)
        x, y, z = ustruct.unpack('<3h', data)
        if raw:
            return x, y, z  # raw readings
        else:
            return x * 0.004, y * 0.004, z * 0.004  # readings in g (assuming full resolution)

    @staticmethod
    # Calculate the magnitude of acceleration
    def calc_accel_magnitude(x, y, z):
        return math.sqrt(x ** 2 + y ** 2 + z ** 2)

    @staticmethod
    # Calculate roll angle in degrees
    def calc_roll(x, y, z):
        return math.atan2(y, math.sqrt(x ** 2 + z ** 2)) * (180 / math.pi)

    @staticmethod
    # Calculate pitch angle in degrees
    def calc_pitch(x, y, z):
        return math.atan2(-x, math.sqrt(y ** 2 + z ** 2)) * (180 / math.pi)


"""
# Interrupt example
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
"""