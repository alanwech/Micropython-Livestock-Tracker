from machine import Pin, I2C
import time
import ustruct
import math
import micropython

micropython.alloc_emergency_exception_buf(100) # Neccesary for raising exceptions during interruptions
 
# Constants
ADXL345_ID = 0x53 # The I2C ID address

ADXL345_POWER_CTL = 0x2D
ADXL345_DATA_FORMAT = 0x31
ADXL345_BW_RATE = 0x2C
ADXL345_DATAX0 = 0x32
ADXL345_THRESH_ACT = 0x24
ADXL345_INT_ENABLE = 0x2E
ADXL345_INT_SOURCE = 0x30
ADXL345_ACT_INACT_CTL = 0x27


# Initialize I2C
i2c = I2C(sda=Pin(21), scl=Pin(22), freq=100000) # Can use SoftI2C alternatively

def write_adxl(address, data): # register address as hex, data as bytearray
    i2c.writeto_mem(ADXL345_ID, address, data)

def read_adxl(address, nbytes): # register address as hex, nbytes as int
    ret = i2c.readfrom_mem(ADXL345_ID, address, nbytes)
    return ret

# Initialize ADXL345, 4mg/LSB -> x = 245~0.98g
def init_adxl345():
    #i2c.writeto_mem(ADXL345_ID, ADXL345_POWER_CTL, bytearray([0x08]))  
    #i2c.writeto_mem(ADXL345_ID, ADXL345_DATA_FORMAT, bytearray([0x0B]))  # Set data format to 
    #i2c.writeto_mem(ADXL345_ID, ADXL345_BW_RATE, bytearray([0x]))  # Set data format
    write_adxl(ADXL345_DATA_FORMAT, bytearray([0x09])) # Full resolution; 0x09 for +-4g; 0x0B for +/- 16g
    write_adxl(ADXL345_POWER_CTL, bytearray([0x08])) # Set bit 3 to 1 to enable measurement mode
    #write_adxl(ADXL345_BW_RATE, bytearray([0x19])) # Set low power mode and ODR to 50Hz
    write_adxl(ADXL345_BW_RATE, bytearray([0x16])) # Set low power mode and ODR to 25Hz
    write_adxl(ADXL345_THRESH_ACT, bytearray([0x07])) # 62.5 mg/LSB -> triggers at 0,4375g
    write_adxl(ADXL345_INT_ENABLE, bytearray([0x10])) # Enable Activity interrumption
    write_adxl(ADXL345_ACT_INACT_CTL, bytearray([0xE0])) # Activity ac mode, enable only XY axis for detection
    
# Read acceleration data
def read_accel_data(raw=False):
    read_adxl(ADXL345_INT_SOURCE, 1) # Clear interruption flags? or does normal read already do that
    data = read_adxl(ADXL345_DATAX0, 6)
    x, y, z = ustruct.unpack('<3h', data)
    if raw:
        return x, y, z # raw readings
    else:
        return x*0.004, y*0.004, z*0.004 # readings in g (asuming full resolution)
 
# Calculate the magnitude of acceleration
def calc_accel_magnitude(x, y, z):
    return math.sqrt(x**2 + y**2 + z**2)
 
# Calculate roll angle in degrees
def calc_roll(x, y, z):
    return math.atan2(y, math.sqrt(x**2 + z**2)) * (180 / math.pi)
 
# Calculate pitch angle in degrees
def calc_pitch(x, y, z):
    return math.atan2(-x, math.sqrt(y**2 + z**2)) * (180 / math.pi)

pin = Pin(23, Pin.IN)
def handle_interrupt(pin):
    print("INT MADE")
    
pin.irq(trigger=Pin.IRQ_RISING, handler=handle_interrupt)


# Main loop
init_adxl345()
while True:
    x, y, z = read_accel_data()
    magnitude = calc_accel_magnitude(x, y, z)
    roll = calc_roll(x, y, z)
    pitch = calc_pitch(x, y, z)
    print("X: {:.1f}g, Y: {:.1f}g, Z: {:.1f}g, Magnitude: {:.2f}g, Roll: {:.2f}, Pitch: {:.2f}".format(x, y, z, magnitude, roll, pitch))
    time.sleep(0.6)
