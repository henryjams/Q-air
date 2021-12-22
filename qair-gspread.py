"""
Qiar air quality module
"""

# general imports
import datetime, time

# imports for google spreadsheet
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# imports for air quality module
import board
import busio
import digitalio
from adafruit_pm25.i2c import PM25_I2C

# imports for GPIO
import RPi.GPIO as GPIO

# Gspread backend
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('qair-pi.json', scope) 
client = gspread.authorize(creds)
sheet = client.open("Qair-pi").sheet1

# GPIO setup
reset_pin = None
button = 36
redLED = 16
bluLED = 18
grnLED = 22

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

GPIO.setup(redLED, GPIO.OUT)
GPIO.setup(bluLED, GPIO.OUT)
GPIO.setup(grnLED, GPIO.OUT)
GPIO.setup(button, GPIO.IN, pull_up_down = GPIO.PUD_UP)

GPIO.output(grnLED, GPIO.HIGH)

# Air quality module backend
# Create library object, use 'slow' 100KHz frequency!
i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)

# Connect to a PM2.5 sensor over I2C
pm25 = PM25_I2C(i2c, reset_pin)

try:
    GPIO.wait_for_edge(button, GPIO.FALLING)
    while True:
        GPIO.output(grnLED, GPIO.LOW)
        GPIO.output(bluLED, GPIO.HIGH)
        time.sleep(1)
        GPIO.output(bluLED, GPIO.LOW)
        try:
            aqdata = pm25.read()
            # print(aqdata)
        except RuntimeError:
            print("Unable to read from sensor, retrying...")
            continue
        data = [aqdata["particles 03um"],
                aqdata["particles 05um"],
                aqdata["particles 10um"]]
        sheet.append_row(data)

except KeyboardInterrupt:
    GPIO.cleanup()
GPIO.cleanup()

