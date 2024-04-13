from typing import Callable, Literal, NewType, Union


_BOART_T = NewType("_BOART_T", object)
BOARD: _BOART_T = object()

_BCM_T = NewType("_BCM_T", object)
BCM: _BCM_T = object()

_IN_T = NewType("_IN_T", object)
IN: _IN_T = object()
_OUT_T = NewType("_OUT_T", object)
OUT: _OUT_T = object()

_HIGH_T = NewType("_HIGH_T", Literal[True])
HIGH: _HIGH_T = object()
_LOW_T = NewType("_LOW_T", Literal[False])
LOW: _LOW_T = object()

_PUD_UP_T = NewType("_PUD_UP_T", object)
PUD_UP: _PUD_UP_T = object()
_PUD_DOWN_T = NewType("_PUD_DOWN_T", object)
PUD_DOWN: _PUD_DOWN_T = object()

_RISING_T = NewType("_RISING_T", object)
RISING: _RISING_T = object()
_FALLING_T = NewType("_FALLING_T", object)
FALLING: _FALLING_T = object()
_BOTH_T = NewType("_BOTH_T", object)
BOTH: _BOTH_T = object()


def setmode(mode: Union[_BOART_T, _BCM_T]) -> None: ...


def setup(
    channel: Union[int, list[int]],
    mode: Union[_IN_T, _OUT_T],
    *,
    initial: Union[_HIGH_T, _LOW_T, None] = None,
    pull_up_down: Union[_PUD_DOWN_T, _PUD_UP_T, None] = None,
) -> None: ...


def input(channel: int) -> Union[_HIGH_T, _LOW_T]: ...


def wait_for_edge(
    chanel: int,
    direction: Union[_RISING_T, _FALLING_T, _BOTH_T],
    *,
    timeout_ms: int = -1,
) -> Union[None, int]: ...


def add_event_detect(
    chanel: int,
    direction: Union[_RISING_T, _FALLING_T, _BOTH_T],
    callback: Callable[[int], None],
) -> None: ...


def add_event_callback(channel: int, callback: Callable[[int], None], bouncetime: int) -> None: ...


def output(channel: int, value: Union[_HIGH_T, _LOW_T]) -> None: ...


def cleanup() -> None: ...
