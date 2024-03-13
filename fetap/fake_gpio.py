from typing import Callable, Literal


BOARD = "BOARD"
BCM = "BCM"

IN = "IN"
OUT = "OUT"

HIGH = "HIGH"
LOW = "LOW"

PUD_UP = "PUD_UP"
PUD_DOWN = "PUD_DOWN"

RISING = "RISING"
FALLING = "FALLING"
BOTH = "BOTH"


def setmode(mode: Literal["BOARD"] | Literal["BCM"]) -> None: ...


def setup(
    channel: int | list[int],
    mode: Literal["IN"] | Literal["OUT"],
    *,
    initial: Literal["HIGH"] | Literal["LOW"] | None = None,
    pull_up_down: Literal["PUD_DOWN"] | Literal["PUD_UP"] | None = None,
) -> None: ...


def wait_for_edge(
    chanel: int,
    direction: Literal["RISING"] | Literal["FALLING"] | Literal["BOTH"],
    *,
    timeout_ms: int = -1,
) -> None | int: ...


def add_event_detect(
    chanel: int,
    direction: Literal["RISING"] | Literal["FALLING"] | Literal["BOTH"],
    callback: Callable[[int], None],
) -> None: ...


def add_event_callback(channel: int, callback: Callable[[int], None]) -> None: ...


def output(channel: int, value: Literal["HIGH"] | Literal["LOW"]) -> None: ...


def cleanup() -> None: ...
