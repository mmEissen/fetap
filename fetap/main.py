from __future__ import annotations
import contextlib

import enum
from typing import TYPE_CHECKING, Callable, Iterable, Protocol
from statemachine import StateMachine, State
import queue

import logging

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    import fetap.fake_gpio as gpio
else:
    try:
        import RPi.GPIO as gpio
    except ImportError:
        log.warning("Using fake GPIO")
        from unittest import mock
        gpio = mock.Mock()


class Phone(StateMachine):
    idle = State(initial=True)
    awaiting_dial_input = State()
    dial_active = State()
    connecting = State()
    ringing = State()
    in_call = State()

    pick_up_receiver = idle.to(awaiting_dial_input) | ringing.to(in_call)
    number_dialed = awaiting_dial_input.to(in_call)
    hang_up = (
        in_call.to(idle)
        | awaiting_dial_input.to(idle)
        | connecting.to(idle)
        | dial_active.to(idle)
    )
    activate_dial = awaiting_dial_input.to(dial_active)
    deactivate_dial = dial_active.to(
        awaiting_dial_input, unless="is_last_digit"
    ) | dial_active.to(connecting, cond="is_last_digit")
    call_connected = connecting.to(in_call)
    dial_pulse = dial_active.to(dial_active, internal=True)
    call_received = idle.to(ringing)

    def __init__(self, number_length: int = 6):
        self.current_dial_digit = 0
        self.dialed_number = ""
        self.number_length = number_length
        super().__init__()

    def on_enter_dial_active(self) -> None:
        self.current_dial_digit = 0

    def after_dial_pulse(self) -> None:
        self.current_dial_digit += 1
        self.current_dial_digit %= 10

    def on_exit_dial_active(self) -> None:
        self.dialed_number += str(self.current_dial_digit)

    def after_hang_up(self) -> None:
        self.dialed_number = ""

    def is_last_digit(self) -> bool:
        if self.dialed_number and self.dialed_number[0] == "0":
            # reserving 0 prefix numbers for now
            return False
        return len(self.dialed_number) == self.number_length


class PhoneEvent(Protocol):
    def __call__(self, phone: Phone) -> None: ...


class _Event:
    def __call__(self, phone: Phone) -> None: 
        return NotImplemented


class Event(_Event, enum.Enum):
    RECEIVER_UP = Phone.pick_up_receiver
    RECEIVER_DOWN = Phone.hang_up
    DIAL_ACTIVATE = Phone.activate_dial
    DIAL_DEACTIVATE = Phone.deactivate_dial
    DIAL_PULSE = Phone.dial_pulse
    INCOMING_CALL = Phone.call_received
    CALL_CONNECTED = Phone.call_connected


class HardwareProtocol(Protocol):
    def setup(self) -> None: ...
    def cleanup(self) -> None: ...


class Hardware:
    PIN_RECEIVER = 26
    PIN_DIAL_ACTIVE = 22
    PIN_DIAL_PULSE = 27
    PIN_RING = 17
    PIN_MODE = gpio.BCM

    def __init__(self, event_queue: queue.Queue[PhoneEvent]) -> None:
        self.event_queue = event_queue

    def setup(self) -> None:
        gpio.setmode(gpio.BCM)

        gpio.setup(self.PIN_RECEIVER, gpio.IN, pull_up_down=gpio.PUD_DOWN)
        gpio.add_event_detect(self.PIN_RECEIVER, gpio.BOTH)
        gpio.add_event_callback(self.PIN_RECEIVER, self.on_receiver_toggle)

        gpio.setup(self.PIN_DIAL_ACTIVE, gpio.IN, pull_up_down=gpio.PUD_DOWN)
        gpio.add_event_detect(self.PIN_DIAL_ACTIVE, gpio.BOTH)
        gpio.add_event_callback(self.PIN_DIAL_ACTIVE, self.on_dial_active_toggle)

        gpio.setup(self.PIN_DIAL_PULSE, gpio.IN, pull_up_down=gpio.PUD_DOWN)
        gpio.add_event_detect(self.PIN_DIAL_PULSE, gpio.RISING)
        gpio.add_event_callback(self.PIN_DIAL_PULSE, self.on_dial_pulse_rising)

        gpio.setup(self.PIN_RING, gpio.OUT, initial=gpio.LOW)

    def cleanup(self) -> None:
        gpio.cleanup()

    def on_dial_active_toggle(self, chanel: int) -> None:
        # This is error prone, because the is executed slightly
        # after the edge was detected. This means that at this point
        # the event may have re-triggered. THis most likely doesn't matter
        # because the timings aren't super tight on those old phones.
        if gpio.input(chanel) == gpio.HIGH:
            self.event_queue.put_nowait(Event.DIAL_ACTIVATE)
        else:
            self.event_queue.put_nowait(Event.DIAL_DEACTIVATE)

    def on_dial_pulse_rising(self, chanel: int) -> None:
        self.event_queue.put_nowait(Event.DIAL_PULSE)

    def on_receiver_toggle(self, chanel: int) -> None:
        # See comment on on_dial_active_toggle
        if gpio.input(chanel) == gpio.HIGH:
            self.event_queue.put_nowait(Event.RECEIVER_UP)
        else:
            self.event_queue.put_nowait(Event.RECEIVER_DOWN)
    


class App:
    PIN_RECEIVER = 26
    PIN_DIAL_ACTIVE = 22
    PIN_DIAL_PULSE = 27
    PIN_RING = 17
    PIN_MODE = gpio.BCM

    def __init__(self, _hardware_factory: Callable[[queue.Queue], HardwareProtocol] = Hardware) -> None:
        self.phone = Phone()
        self.event_queue: queue.Queue[Event] = queue.Queue()
        self.hardware = _hardware_factory(self.event_queue)

    def start(self) -> None:
        self.hardware.setup()

    def stop(self) -> None:
        self.hardware.cleanup()

    def run_forever(self) -> None:
        while True:
            self.handle_next_event()

    def handle_next_event(self) -> None:
        event = self.event_queue.get()
        event(self.phone)


@contextlib.contextmanager
def phone_app() -> Iterable[App]:
    app = App()
    app.start()

    try:
        yield app
    finally:
        app.stop()




