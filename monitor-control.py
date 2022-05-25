#!/usr/bin/python3

from sys import stdout
import RPi.GPIO as GPIO
from time import sleep, time
import cec


#################
#  Definitions  #
#################

GPIO.setmode(GPIO.BOARD)

GPIO.setup(18, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

def print_(content):
    print(content)
    stdout.flush()  # Flush output buffer after each
                    # print for proper logging on Linux


##########
#  Main  #
##########

print_("Monitor control started.")

try:
    cec.init()
    print_("Init successful.")
except Exception as e:
    print_("Init failed: " + str(e))
    print_("Monitor control exiting...")
    exit()

cec_tv = cec.Device(cec.CECDEVICE_TV)

currentTime = 0
referenceTime = 0
elapsedTime = 0

try:

    while True:

        currentTime = time()

        if GPIO.input(18) != 0:

            elapsedTime += currentTime - referenceTime

            if elapsedTime > .05:

                try:
                    if cec_tv.is_on():
                        cec_tv.standby()
                        print_("Turned monitor off.")
                    else:
                        cec_tv.power_on()
                        print_("Turned monitor on.")
                except Exception as e:
                    print_("Toggling power failed: " + str(e))

                sleep(.5)

        else:

            elapsedTime = 0

        referenceTime = currentTime

except KeyboardInterrupt:

    GPIO.cleanup()
    print_("Monitor control exiting...")