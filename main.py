# Temp and Humidity sensor
# Harry Hollies
# 17/02/2024

from machine import Pin, I2C
from time import sleep, sleep_ms

import network
import socket

# Run this code to find out what the address is of the temperature sensor
# Return a decimal number, needs converting to hexadecimal
i2c = I2C(0, scl=Pin(5), sda=Pin(4), freq=400000)
print(i2c.scan())

# Filter out the address of the SHT31 sensor
sht31_address = 0x45
other_devices = [addr for addr in i2c.scan() if addr != sht31_address]

print("Other devices found on the I2C bus:")
for addr in other_devices:
    print(f"Address: 0x{addr:02x}")


#-----------------------------------------------------------------------------------------------


R_HIGH   = const(1)
R_MEDIUM = const(2)
R_LOW    = const(3)

class SHT31(object):
    """
    This class implements an interface to the SHT31 temprature and humidity
    sensor from Sensirion.
    """

    # This static map helps keeping the heap and program logic cleaner
    _map_cs_r = {
    	True: {
            R_HIGH : b'\x2c\x06',
            R_MEDIUM : b'\x2c\x0d',
            R_LOW: b'\x2c\x10'
            },
        False: {
            R_HIGH : b'\x24\x00',
            R_MEDIUM : b'\x24\x0b',
            R_LOW: b'\x24\x16'
            }
        }

    def __init__(self, i2c, addr=0x45): # Check address of your sensor
        """
        Initialize a sensor object on the given I2C bus and accessed by the
        given address.
        """
        if i2c == None:
            raise ValueError('I2C object needed as argument!')
        self._i2c = i2c
        self._addr = addr

    def _send(self, buf):
        """
        Sends the given buffer object over I2C to the sensor.
        """
        self._i2c.writeto(self._addr, buf)

    def _recv(self, count):
        """
        Read bytes from the sensor using I2C. The byte count can be specified
        as an argument.
        Returns a bytearray for the result.
        """
        return self._i2c.readfrom(self._addr, count)

    def _raw_temp_humi(self, r=R_HIGH, cs=True):
        """
        Read the raw temperature and humidity from the sensor and skips CRC
        checking.
        Returns a tuple for both values in that order.
        """
        if r not in (R_HIGH, R_MEDIUM, R_LOW):
            raise ValueError('Wrong repeatabillity value given!')
        self._send(self._map_cs_r[cs][r])
        sleep_ms(100)
        raw = self._recv(6)
        return (raw[0] << 8) + raw[1], (raw[3] << 8) + raw[4]

    def get_temp_humi(self, resolution=R_HIGH, clock_stretch=True, celsius=True):
        """
        Read the temperature in degree celsius or fahrenheit and relative
        humidity. Resolution and clock stretching can be specified.
        Returns a tuple for both values in that order.
        """
        t, h = self._raw_temp_humi(resolution, clock_stretch)
        if celsius:
            temp = -45 + (175 * (t / 65535))
        else:
            temp = -49 + (315 * (t / 65535))
        return temp, 100 * (h / 65535)


#-----------------------------------------------------------------------------------------
# If using Pico, print(get_temp_humi()) to display sensor readings
#-----------------------------------------------------------------------------------------


# Configure Newtwork (Pico W Only)

ssid = '************'
password = '************'


def connect():
    blue = Pin(6, Pin.OUT)

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('connecting to network...')
        # Flash led quickly to show connection is working
        blue.value(1)  # set GPIO pin high (turn on LED)
        sleep(0.25)
        blue.value(0)  # set GPIO pin low (turn off LED)
        sleep(0.25)
        blue.value(1)  # set GPIO pin high (turn on LED)
        sleep(0.25)
        blue.value(0)  # set GPIO pin low (turn off LED)
        sleep(0.25)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip


def isConnected():
    wlan = network.WLAN(network.STA_IF)
    return wlan.isconnected()


def open_socket(ip):
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(2) # max number of connections
    print(f"Listeneing on {address}")
    return connection


# Generate webpage, refresh content every 60 seconds
def webpage(reading):
    html = f"""
        <!DOCTYPE HTML>
            <html lang="en">
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="initial-scale=1, minimal-ui, width=device-width">
                    <title>Pico W Temp / Humidity</title>
                    <meta http-equiv="refresh" content="60">
                </head>
                <body>
                    <main>
                        <div style= "text-align:center; font-size:30px;">
                            <p id="reading" name="reading">{reading}</p>
                        </div>
                    </main>
                    <footer>
                    </footer>
                </body>
            </html>
        """
    return str(html)


def serve(connection):
    # Start web server    
    while True:
        try:
            # Validate Data received from sensor
            temp = sensor.get_temp_humi()[0]
            humi = sensor.get_temp_humi()[1]
            if isinstance(temp, float) and isinstance(humi, float):
                temp = int(temp)
                humi = int(humi)
                if temp > -5 and  temp < 70 and humi >= 0 and humi <= 99:
                    
                    # Data passed validation, Send data!
                    sensor_data = {'Temp': temp, 'Humidity': humi}
                    print(sensor_data)
                    client = connection.accept()[0]
                    request = client.recv(1024)
                    html = webpage(sensor_data)
                    client.send(html)
                    
                    # Slow flash led to show the program is working
                    blue.value(0)
                    sleep(1)
                    blue.value(1)
                    sleep(2)
                    blue.value(0)
                    sleep(1)
                    blue.value(1)
                    sleep(2)
                    client.close()
                else:
                    print("Invalid data from sensor")
                    continue
            else:
                print("Invalid data from sensor")
                continue
        except Exception as e:
            print(f"Error sending data {e}")
            blue.value(0)
            sleep(2)
            serve(connection)

#-----------------------------------------------------------------------------------------


blue = Pin(6, Pin.OUT)
sensor = SHT31(i2c, addr=0x45)

# Check wifi connected and render webpage accessed on local IP of Pico W
while True:
    if not isConnected():
        blue.value(0)
        ip = connect()
    else:
        blue.value(1)
        connection = open_socket(ip)
        serve(connection)
