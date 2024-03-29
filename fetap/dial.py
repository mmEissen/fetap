
import threading
from typing import TYPE_CHECKING

import logging
import time

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    import fetap.fake_gpio as gpio
else:
    try:
        import RPi.GPIO as gpio
    except ImportError:
        log.warning("Using fake GPIO")
        import fetap.fake_gpio as gpio


def get_number() -> None:
    print("Setup")
    gpio.setmode(gpio.BOARD)
    PIN_IMPULSE = 13
    PIN_ENABLE = 11

    gpio.setup(PIN_ENABLE, gpio.IN, pull_up_down=gpio.PUD_DOWN)
    gpio.setup(PIN_IMPULSE, gpio.IN, pull_up_down=gpio.PUD_DOWN)
    counter_lock = threading.Lock()
    counter = 0

    def impulse(chanel: int) -> None:
        nonlocal counter
        with counter_lock:
            counter += 1
            counter %= 10
    
    gpio.add_event_detect(PIN_IMPULSE, gpio.RISING)
    gpio.add_event_callback(PIN_IMPULSE, impulse)

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
    PIN = 15

    gpio.setup(PIN, gpio.OUT, initial=gpio.LOW)

    for _ in range(N):
        for _ in range(int(RING_TIME / (ON_TIME + OFF_TIME))):
            gpio.output(PIN, gpio.HIGH)
            time.sleep(ON_TIME)
            gpio.output(PIN, gpio.LOW)
            time.sleep(OFF_TIME)
        time.sleep(PAUSE_TIME)



