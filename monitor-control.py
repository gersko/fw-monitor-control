#!/usr/bin/python3

from sys import stdout
import RPi.GPIO as GPIO
import time
import cec
import http.server
import socketserver
import threading


#################
#  Definitions  #
#################

GPIO.setmode(GPIO.BOARD)

GPIO.setup(18, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

def print_(content):
    print(content)
    stdout.flush()  # Flush output buffer after each print for proper logging on Linux

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global http_action
        if self.path == "/monitor?turn=on":
            print_("HTTP request: turn monitor on.")
            http_action = "turn_on"
            self.send_response(200)
        elif self.path == "/monitor?turn=off":
            print_("HTTP request: turn monitor off.")
            http_action = "turn_off"
            self.send_response(200)
        else:
            self.send_response(400)

def server_thread_target():
    while True:
        try:
            with socketserver.TCPServer(("", 8080), RequestHandler) as httpd:
                print_("HTTP server started.")
                httpd.serve_forever()
        except Exception as e:
            print_("HTTP server failed: " + str(e))
            print_("Restarting HTTP server in 10s...")
            time.sleep(10)

def toggle_monitor(action=None):
    if action is None:
        if cec_tv.is_on():
            action = "turn_off"
        else:
            action = "turn_on"
    try:
        if action == "turn_off":
            print_("Turning monitor off...")
            cec_tv.standby()
        elif action == "turn_on":
            print_("Turning monitor on...")
            cec_tv.power_on()
    except Exception as e:
        print_("Toggling monitor failed: " + str(e))


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

http_action = None  # Pending action via http (always reset to None if no action is pending)

server_thread = threading.Thread(target=server_thread_target, daemon=True)
server_thread.start()

time_current = 0

time_button_last_off = time_current
time_button_last_action = 0

time_http_last_action = 0

while True:

    time_current = time.time()

    # Toggle monitor via push-button
    if GPIO.input(18) == 0:
        time_button_last_off = time_current
    else:
        if (
            time_current - time_button_last_off >= .05 and
            time_current - time_button_last_action >= 1
        ):
            time_button_last_action = time_current
            print_("Push-button: toggle monitor.")
            toggle_monitor()

    # Toggle monitor via HTTP request
    if not http_action is None:
        if time_current - time_http_last_action >= 1:
            time_http_last_action = time_current
            try:
                if http_action == "turn_on":
                    if cec_tv.is_on():
                        http_action = None
                    else:
                        toggle_monitor("turn_on")
                elif http_action == "turn_off":
                    if not cec_tv.is_on():
                        http_action = None
                    else:
                        toggle_monitor("turn_off")
            except OSError:
                pass

    time.sleep(.01)
