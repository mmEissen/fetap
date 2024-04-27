from __future__ import annotations
import contextlib

import enum
import subprocess
import sys
import time
from typing import Callable, Iterable, Protocol
from statemachine import StateMachine, State
from statemachine.exceptions import TransitionNotAllowed
import queue

import logging

from fetap.storage import PhoneBook

log = logging.getLogger(__name__)

from fetap.conman import gpio
from fetap import pjsua


def noop() -> None:
    return

class Phone(StateMachine):
    idle = State(initial=True)
    awaiting_dial_input = State()
    dial_active = State()
    connecting = State()
    ringing = State()
    in_call = State()
    disconnected = State()

    pick_up_receiver = idle.to(awaiting_dial_input) | ringing.to(in_call)
    receiver_down = (
        in_call.to(idle)
        | awaiting_dial_input.to(idle)
        | connecting.to(idle)
        | dial_active.to(idle)
        | disconnected.to(idle)
    )
    counter_party_hang_up = in_call.to(disconnected) | ringing.to(idle)
    activate_dial = awaiting_dial_input.to(dial_active)
    deactivate_dial = dial_active.to(
        awaiting_dial_input, unless="is_last_digit"
    ) | dial_active.to(connecting, cond="is_last_digit")
    call_connected = connecting.to(in_call)
    dial_pulse = dial_active.to(dial_active, internal=True)
    call_received = idle.to(ringing)

    def __init__(self, pjsua_: pjsua.PJSua, number_length: int = 6):
        self.current_dial_digit = 10
        self.dialed_number = ""
        self.number_length = number_length
        self.pjsua = pjsua_
        super().__init__()

    def on_enter_dial_active(self) -> None:
        self.current_dial_digit = 10

    def on_enter_connecting(self) -> None:
        if self.dialed_number == "1231234":
            self.pjsua.call("192.168.2.223")

    def after_dial_pulse(self) -> None:
        self.current_dial_digit += 1
        self.current_dial_digit %= 10

    def on_exit_dial_active(self) -> None:
        if self.current_dial_digit == 10:
            return
        self.dialed_number += str(self.current_dial_digit)

    def after_receiver_down(self) -> None:
        self.dialed_number = ""

    def on_exit_in_call(self) -> None:
        self.pjsua.hangup_all()

    def is_last_digit(self) -> bool:
        return len(self.dialed_number) == self.number_length


class PhoneEvent(Protocol):
    def __call__(self, phone: Phone) -> None: ...


class _Event:
    def __init__(self, callback: Callable[[Phone], None]) -> None:
        self.callback = callback


class Event(_Event, enum.Enum):
    RECEIVER_UP = (Phone.pick_up_receiver,)
    RECEIVER_DOWN = (Phone.receiver_down,)
    DIAL_ACTIVATE = (Phone.activate_dial,)
    DIAL_DEACTIVATE = (Phone.deactivate_dial,)
    DIAL_PULSE = (Phone.dial_pulse,)
    INCOMING_CALL = (Phone.call_received,)
    CALL_CONNECTED = (Phone.call_connected,)
    COUNTER_PARTY_HANG_UP = (Phone.counter_party_hang_up,)

    def make_callback_for(self, event_queue: queue.Queue[Event]) -> Callable[[], None]:
        def _callback(*args: object) -> None:
            event_queue.put_nowait(self)
        return _callback


class HardwareProtocol(Protocol):
    def setup(self) -> None: ...
    def cleanup(self) -> None: ...


class Hardware:
    PIN_RECEIVER = 26
    PIN_DIAL_ACTIVE = 27
    PIN_DIAL_PULSE = 22
    PIN_RING = 17
    PIN_MODE = gpio.BCM

    def __init__(
        self,
        on_receiver_down: Callable[[], None] = noop,
        on_receiver_up: Callable[[], None] = noop,
        on_dial_activate: Callable[[], None] = noop,
        on_dial_deactivate: Callable[[], None] = noop,
        on_dial_pulse: Callable[[], None] = noop,
    ) -> None:
        self.on_receiver_down = on_receiver_down
        self.on_receiver_up = on_receiver_up
        self.on_dial_activate = on_dial_activate
        self.on_dial_deactivate = on_dial_deactivate
        self.on_dial_pulse = on_dial_pulse

    def setup(self) -> None:
        gpio.setmode(gpio.BCM)

        gpio.setup(self.PIN_RECEIVER, gpio.IN, pull_up_down=gpio.PUD_DOWN)
        gpio.add_event_detect(self.PIN_RECEIVER, gpio.BOTH, bouncetime=50)
        gpio.add_event_callback(self.PIN_RECEIVER, self.on_receiver_toggle)

        gpio.setup(self.PIN_DIAL_ACTIVE, gpio.IN, pull_up_down=gpio.PUD_DOWN)
        gpio.add_event_detect(self.PIN_DIAL_ACTIVE, gpio.BOTH, bouncetime=100)
        gpio.add_event_callback(self.PIN_DIAL_ACTIVE, self.on_dial_active_toggle)

        gpio.setup(self.PIN_DIAL_PULSE, gpio.IN, pull_up_down=gpio.PUD_DOWN)
        gpio.add_event_detect(self.PIN_DIAL_PULSE, gpio.FALLING, bouncetime=40)
        gpio.add_event_callback(self.PIN_DIAL_PULSE, self.on_dial_pulse)

        gpio.setup(self.PIN_RING, gpio.OUT, initial=gpio.LOW)

    def cleanup(self) -> None:
        gpio.cleanup()

    def on_dial_active_toggle(self, chanel: int) -> None:
        # This is error prone, because the is executed slightly
        # after the edge was detected. This means that at this point
        # the event may have re-triggered. This most likely doesn't matter
        # because the timings aren't super tight on those old phones.
        if gpio.input(chanel) == gpio.HIGH:
            self.on_dial_activate()
        else:
            self.on_dial_deactivate()

    def on_dial_pulse(self, chanel: int) -> None:
        self.on_dial_pulse()

    def on_receiver_toggle(self, chanel: int) -> None:
        # See comment on on_dial_active_toggle
        if gpio.input(chanel) == gpio.HIGH:
            self.on_receiver_up()
        else:
            self.on_receiver_down()


class App:
    PIN_RECEIVER = 26
    PIN_DIAL_ACTIVE = 22
    PIN_DIAL_PULSE = 27
    PIN_RING = 17
    PIN_MODE = gpio.BCM

    def __init__(
        self,
        event_queue: queue.Queue[Event],
        phone: Phone,
        pjsua_: pjsua.PJSua,
        hardware: Hardware,
        phone_book: PhoneBook,
    ) -> None:
        self.event_queue = event_queue
        self.phone = phone
        self.pjsua = pjsua_
        self.hardware = hardware

    def start(self) -> None:
        self.hardware.setup()
        self.pjsua.start()

    def stop(self) -> None:
        self.hardware.cleanup()
        self.pjsua.stop()

    def run_forever(self) -> None:
        while True:
            self.handle_next_event()

    def handle_next_event(self) -> None:
        event = self.event_queue.get()
        log.debug(f"Hardware event: {event.name}")
        try:
            event.callback(self.phone)
        except TransitionNotAllowed:
            log.debug(
                f"Transition {event.name} is not allowed in {self.phone.current_state.name}, skipping"
            )


@contextlib.contextmanager
def config_server(phone_book_path: str) -> Iterable[None]:
    subprocess.Popen(
        [
            sys.executable,
            "-m",
            "flask",
            "--app",
            "fetap.web_server",
            "run",
            "--host=0.0.0.0",
            "--port=80",
        ],
        env={"PHONE_BOOK": phone_book_path}
    )
    try:
        yield
    finally:
        pass


@contextlib.contextmanager
def phone_app(
    event_queue: queue.Queue[Event],
    phone: Phone,
    pjsua_: pjsua.PJSua,
    hardware: Hardware,
    phone_book: PhoneBook,
) -> Iterable[App]:
    app = App(
        event_queue=event_queue,
        phone=phone,
        pjsua_=pjsua_,
        hardware=hardware,
        phone_book=phone_book,
    )
    app.start()

    try:
        yield app
    finally:
        app.stop()


@contextlib.contextmanager
def create_app(phone_book_path: str = "phone_book.json") -> Iterable[App]:
    log.debug("Creating App")
    event_queue: queue.Queue[Event] = queue.Queue()
    pjsua_ = pjsua.PJSua(
        on_incoming_call=Event.INCOMING_CALL.make_callback_for(event_queue),
        on_call_connected=Event.CALL_CONNECTED.make_callback_for(event_queue),
        on_call_hangup=Event.COUNTER_PARTY_HANG_UP.make_callback_for(event_queue),
    )
    phone: Phone = Phone(pjsua_=pjsua_)
    hardware = Hardware(
        on_dial_activate=Event.DIAL_ACTIVATE.make_callback_for(event_queue),
        on_dial_deactivate=Event.DIAL_DEACTIVATE.make_callback_for(event_queue),
        on_dial_pulse=Event.DIAL_PULSE.make_callback_for(event_queue),
        on_receiver_down=Event.RECEIVER_DOWN.make_callback_for(event_queue),
        on_receiver_up=Event.RECEIVER_UP.make_callback_for(event_queue),
    )
    phone_book = PhoneBook(file_path=phone_book_path)

    with config_server(phone_book_path), phone_app(
        event_queue, phone, pjsua_, hardware, phone_book
    ) as app:
        yield app


def hardware_test() -> None:
    hardware = Hardware(
        on_dial_activate=lambda: print("dial_activate"),
        on_dial_deactivate=lambda: print("dial_deactivate"),
        on_dial_pulse=lambda: print("dial_pulse"),
        on_receiver_down=lambda: print("receiver_down"),
        on_receiver_up=lambda: print("receiver_up"),
    )
    hardware.setup()
    try:
        time.sleep(9999)
    finally:
        hardware.cleanup()