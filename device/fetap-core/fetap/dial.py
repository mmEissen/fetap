
import threading

import logging
import time

log = logging.getLogger(__name__)

from fetap.conman import gpio


def get_number() -> None:
    print("Setup")
    gpio.setmode(gpio.BCM)
    PIN_IMPULSE = 22
    PIN_ENABLE = 27

    gpio.setup(PIN_ENABLE, gpio.IN, pull_up_down=gpio.PUD_DOWN)
    gpio.setup(PIN_IMPULSE, gpio.IN, pull_up_down=gpio.PUD_DOWN)
    counter_lock = threading.Lock()
    counter = 0

    def impulse(chanel: int) -> None:
        nonlocal counter
        print("pulse")
        with counter_lock:
            counter += 1
            counter %= 10
    
    gpio.add_event_detect(PIN_IMPULSE, gpio.FALLING, callback=impulse, bouncetime=40)
    # gpio.add_event_callback(PIN_IMPULSE, impulse, bouncetime=40)

    print("starting loop")
    while True:
        gpio.wait_for_edge(PIN_ENABLE, gpio.RISING)
        print("enable")
        gpio.wait_for_edge(PIN_ENABLE, gpio.FALLING)
        print("disable")
        with counter_lock:
            print(f"Dial: {counter}")
            if counter == 5:
                ring()
            counter = 0


def ring() -> None:
    print("RING RING RING")
    ON_TIME = 0.01
    OFF_TIME = 0.01
    RING_TIME = 1
    PAUSE_TIME = 1
    N = 3
    PIN = 17

    gpio.setup(PIN, gpio.OUT, initial=gpio.LOW)

    for _ in range(N):
        for _ in range(int(RING_TIME / (ON_TIME + OFF_TIME))):
            gpio.output(PIN, gpio.HIGH)
            time.sleep(ON_TIME)
            gpio.output(PIN, gpio.LOW)
            time.sleep(OFF_TIME)
        time.sleep(PAUSE_TIME)



