"""
Qiar ~ air quality module
"""

# general imports
import datetime, time
from time import sleep

# imports for google spreadsheet
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# imports for air quality module
import board
import busio
from digitalio import DigitalInOut, Direction, Pull
from adafruit_pm25.i2c import PM25_I2C

# imports for GPIO
from gpiozero import LED, Button
from signal import pause

# Gspread backend
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('qair-pi.json', scope) 
client = gspread.authorize(creds)
sheet = client.open("Qair-pi").sheet1

# GPIO setup
reset_pin = None

btn = Button(16)
red = LED(23)
blu = LED(24)
grn = LED(25)

grn.on()

# Air quality module backend
# Create library object, use 'slow' 100KHz frequency!
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

# Connect to a PM2.5 sensor over I2C
pm25 = PM25_I2C(i2c, reset_pin)

"""
This function reads data from the PMSA003i and writes it to a gspreadsheet
A blinking blue LED indicates when measurements are being taken
"""
def qair():
    test_time = 0
    grn.off()
    while test_time < 29:
        blu.on()
        sleep(1)
        try:
            aqdata = pm25.read()
            # print(aqdata)
        except RuntimeError:
            print("Unable to read from sensor, retrying...")
            continue
        data = [aqdata["particles 03um"],
                aqdata["particles 05um"],
                aqdata["particles 10um"]]
        blu.off()
        sheet.append_row(data)
        test_time += 1
    print("Measurements complete.")
    grn.on()

btn.when_pressed = qair

pause()

