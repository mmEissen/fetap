from typing import Iterable, NewType, Union


MIN_DISTANCE = 7
NUMBER_LENGTH = 7
_7_tuple = tuple[int, int, int, int, int, int, int]
PhoneNumber = NewType("PhoneNumber", _7_tuple)
PulseCounts = NewType("PulseCounts", _7_tuple)


def as_pulse_counts(number: Iterable[int]) -> PulseCounts:
    number_tuple = tuple(number)
    if len(number_tuple) != NUMBER_LENGTH:
        raise ValueError(f"Phone numbers must have exactly {NUMBER_LENGTH} digits")
    if any(d < 0 for d in number_tuple):
        raise ValueError(f"All digits must be >= 0")
    return PulseCounts(number_tuple)


def as_phone_number(value: Union[str, Iterable[int]]) -> PhoneNumber:
    if isinstance(value, str):
        return as_phone_number(tuple(int(c) for c in value))

    number_tuple = tuple(value)
    if len(number_tuple) != NUMBER_LENGTH:
        raise ValueError(f"Phone numbers must have exactly {NUMBER_LENGTH} digits")
    if any((d < 0 or d > 9) for d in number_tuple):
        raise ValueError(f"All digits must be in the range 0 to 9")
    return PhoneNumber(number_tuple)


def to_pulse_counts(number: PhoneNumber) -> PulseCounts:
    # The digit 0 is 10 pulses
    return PulseCounts(tuple(d or 10 for d in number))


def find_similar_numbers(
    new_number: PhoneNumber,
    existing_numbers: list[PhoneNumber],
    min_distance: int = MIN_DISTANCE,
) -> list[tuple[PhoneNumber, int]]:
    return find_closest_phone_numbers(
        to_pulse_counts(new_number), existing_numbers, 2 * min_distance
    )


def find_closest_phone_numbers(
    pulse_counts: PulseCounts,
    existing_numbers: list[PhoneNumber],
    min_distance: int = MIN_DISTANCE,
) -> list[tuple[PhoneNumber, int]]:
    distances = (
        _signal_distance(pulse_counts, to_pulse_counts(number))
        for number in existing_numbers
    )
    return [
        (number, distance)
        for number, distance in zip(existing_numbers, distances)
        if distance <= min_distance
    ]


def _signal_distance(left: PulseCounts, right: PulseCounts) -> int:
    """A measure for how different two pulse counts are.
    
    This is essentially a measure in how many miss-counts of pulses there have
    been in the signal.
    """
    return sum(abs(l - r) for l, r in zip(left, right))
