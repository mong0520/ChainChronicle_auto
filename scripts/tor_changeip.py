import requesocks
import time
from stem import Signal
from stem.control import Controller

def renew_connection():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate(password='emanager')
        print("Success!")
        controller.signal(Signal.NEWNYM)
        print("New Tor connection processed")

if __name__ == '__main__':
    while True:
        renew_connection()
        time.sleep(0.1)
