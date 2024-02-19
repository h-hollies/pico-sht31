# SHT31 Temperature and Humidity Project

A project to measure temperature and humidity using a SHT31 sensor. The code is written in micropython, for the PI Pico W!

I was trying to program  a temperature and humidity sensor using the SHT31 sensor. I struggled to find  any good documentation on how to use it, so I decided to create my own project that would help. I started this using thonny and trying to import libraries to help me access the data on the sensor through the Pico W, but nothing seemed to be working as described!

Here is my solution for anybody else struggling to program the SHT31 alongside the Pico / Pico W.

Please find attached my setup on the breadboard.

![Pico W with sht31 sensor](img/20240218_220243.jpg)

## Pins:
- VCC (temp sensor): connect this to 3V on the Pico
- GND (temp sensor): connect this to ground on the Pico
- SCL (temp sensor): connect this to GPIO5 on the Pico
- SDA (temp sensor): connect this to GPIO4 on the pico

- Pin 6 on the Pico goes to the positive on the blue LED
- Ground the negative for the LED

I have bridged a Green LED across the VCC and GND of the SHT31 sensor to indicate there is power going to the sensor.
The Blue LED is controlled by Pin 6 and will flash fast when the Pico is trying to connect to the wifi, once a connection has been made the LED will stay on. The LED will flash slowly when data is being transferred to the website for viewing.

Once the Pico W is running the data can be seen in a webbrowser by typing in the Pico's IP address. The Pico's IP address will be printed in the terminal when you execute the code.

## Please Note:
Read through the code carefully before using it, there are parts that you WILL need to change in order for it to work for you. *i.e ssid and password credentials in config.py / possibly your sensor address could be different!* If you are using the Pico and don't have wifi access, the top half of this code will work. Just comment out everything after the Network Configuration and print the results to the terminal!
