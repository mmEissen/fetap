from typing import Callable, Literal, NewType


_BOART_T = NewType("_BOART_T", object)
BOARD: _BOART_T

_BCM_T = NewType("_BCM_T", object)
BCM: _BCM_T

_IN_T = NewType("_IN_T", object)
IN: _IN_T
_OUT_T = NewType("_OUT_T", object)
OUT: _OUT_T

_HIGH_T = NewType("_HIGH_T", Literal[True])
HIGH: _HIGH_T
_LOW_T = NewType("_LOW_T", Literal[False])
LOW: _LOW_T

_PUD_UP_T = NewType("_PUD_UP_T", object)
PUD_UP: _PUD_UP_T
_PUD_DOWN_T = NewType("_PUD_DOWN_T", object)
PUD_DOWN: _PUD_DOWN_T

_RISING_T = NewType("_RISING_T", object)
RISING: _RISING_T
_FALLING_T = NewType("_FALLING_T", object)
FALLING: _FALLING_T
_BOTH_T = NewType("_BOTH_T", object)
BOTH: _BOTH_T


def setmode(mode: _BOART_T | _BCM_T) -> None: ...


def setup(
    channel: int | list[int],
    mode: _IN_T | _OUT_T,
    *,
    initial: _HIGH_T | _LOW_T | None = None,
    pull_up_down: _PUD_DOWN_T | _PUD_UP_T | None = None,
) -> None: ...


def input(channel: int) -> _HIGH_T | _LOW_T: ...


def wait_for_edge(
    chanel: int,
    direction: _RISING_T | _FALLING_T | _BOTH_T,
    *,
    timeout_ms: int = -1,
) -> None | int: ...


def add_event_detect(
    chanel: int,
    direction: _RISING_T | _FALLING_T | _BOTH_T,
    callback: Callable[[int], None],
) -> None: ...


def add_event_callback(channel: int, callback: Callable[[int], None]) -> None: ...


def output(channel: int, value: _HIGH_T | _LOW_T) -> None: ...


def cleanup() -> None: ...
