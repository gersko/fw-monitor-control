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

def print_(content):
    print(content)
    stdout.flush()  # Flush output buffer after each print
                    # for proper logging on Linux

def cec_init():
    global cec_reinit

    print_("Initializing CEC...")
    success = False
    try:
        cec.init()
        print_("CEC initialization successful.")
        cec_reinit = False
        success = True
    except Exception as e:
        print_(f"CEC initialization failed: {e}")

    return success

def get_monitor_state():
    global cec_reinit

    print_("Retrieving monitor state...")
    state = None
    try:
        if cec_tv.is_on():
            state = "on"
        else:
            state = "off"
        print_(f"Monitor is turned {state}.")
    except OSError as e:
        print_(
            f"Failed to retrieve monitor state: {e}. "
            f"Reinitializing CEC.")
        cec_reinit = True

    return state

def toggle_monitor(action=None):
    global http_action

    print_(f"Toggle monitor (action={action})...")

    cec_tv_state = get_monitor_state()
    if cec_tv_state is None:
        return
    elif (
        (cec_tv_state == "on" and action == "turn_on") or
        (cec_tv_state == "off" and action == "turn_off")
    ):
        http_action = None
        return
    elif cec_tv_state == "on" and action is None:
        action = "turn_off"
    elif cec_tv_state == "off" and action is None:
        action = "turn_on"

    try:
        if action == "turn_off":
            print_("Turning monitor off...")
            cec_tv.standby()
            print_("Successfully sent standby command.")
        elif action == "turn_on":
            print_("Turning monitor on...")
            cec_tv.power_on()
            print_("Successfully sent power on command.")
    except Exception as e:
        print_(f"Toggling monitor failed: {e}.")

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global http_action
        if self.path == "/monitor?turn=on":
            print_(f"HTTP request from {self.client_address[0]}: turn monitor on.")
            http_action = "turn_on"
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Turning monitor on...")
        elif self.path == "/monitor?turn=off":
            print_(f"HTTP request from {self.client_address[0]}: turn monitor off.")
            http_action = "turn_off"
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Turning monitor off...")
        elif self.path == "/monitor?state":
            print_(f"HTTP request from {self.client_address[0]}: retrieve monitor state.")
            cec_tv_state = get_monitor_state()
            if cec_tv_state is None:
                state = (
                    f"Failed to retrieve monitor state. "
                    f"Reinitializing CEC, try again.")
            else:
                state = f"Monitor is turned {cec_tv_state}."
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(str.encode(state))
        else:
            self.send_response(400)

def server_thread_target():
    while True:
        print_("Starting HTTP server...")
        try:
            with socketserver.TCPServer(("", 8080), RequestHandler) as httpd:
                print_("HTTP server started.")
                httpd.serve_forever()
        except OSError as e:
            print_("HTTP server failed: " + str(e))
            print_("Restarting HTTP server in 30s...")
            time.sleep(30)


##########
#  Main  #
##########

cec_reinit = False  # Specifies whether CEC needs to be reinitialized
http_action = None  # Pending action of the latest HTTP request
                    # (always reset to None if no action is pending)

time_button_last_off = 0
time_button_last_action = 0

time_http_last_action = 0

print_("Monitor control started.")

# Initialize CEC
cec_initial_init_fail_count = 0
while not cec_init():
    cec_initial_init_fail_count += 1
    if cec_initial_init_fail_count < 10:
        time.sleep(10)
        continue
    else:
        print_("CEC initialization failed 10 times. Monitor control exiting...")
        exit()
cec_tv = cec.Device(cec.CECDEVICE_TV)
get_monitor_state()

# Turn on monitor before the FF-Agent Status-Monitor RPi boots up
toggle_monitor("turn_on")

# Initialize GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(18, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

# Start HTTP server
server_thread = threading.Thread(target=server_thread_target, daemon=True)
server_thread.start()

while True:

    # Reinitialize CEC if necessary
    if cec_reinit:
        if not cec_init():
            time.sleep(10)
            continue

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
        if time_current - time_http_last_action >= 5:
            time_http_last_action = time_current
            toggle_monitor(http_action)

    time.sleep(.01)
