from typing import Iterable, Union
import pytest
from fetap import error_correction


NUMBERS = [
    error_correction.as_phone_number("0000000"),
    error_correction.as_phone_number("5555555"),
    error_correction.as_phone_number("0987654"),
]


class TestFindClosestPhoneNumbers:
    @pytest.mark.parametrize(
        "pulses",
        [
            error_correction.as_pulse_counts([5, 5, 5, 5, 5, 5, 5]),
            error_correction.as_pulse_counts([6, 4, 6, 4, 6, 4, 6]),
            error_correction.as_pulse_counts([5, 5, 5, 5, 6, 8, 8]),
        ],
    )
    def test_happy_path(self, pulses: error_correction.PulseCounts) -> None:
        result = error_correction.find_closest_phone_numbers(pulses, NUMBERS)

        assert len(result) == 1
        number, error = result[0]
        assert number == error_correction.as_phone_number("5555555")
        assert error <= 7

    @pytest.mark.parametrize(
        "pulses",
        [
            error_correction.as_pulse_counts([6, 4, 6, 4, 6, 4, 7]),
            error_correction.as_pulse_counts([5, 5, 5, 5, 7, 8, 8]),
        ],
    )
    def test_no_similar_numbers(self, pulses: error_correction.PulseCounts) -> None:
        result = error_correction.find_closest_phone_numbers(pulses, NUMBERS)

        assert result == []


class TestAsPulseCounts:
    @pytest.mark.parametrize(
        "pulses",
        [
            (0, 0, 0, 0, 0, 0, 0),
            (10, 10, 10, 10, 10, 10, 10),
            (1, 2, 3, 4, 5, 6, 7),
        ],
    )
    def test_happy_path(self, pulses: tuple[int, ...]) -> None:
        pulse_count = error_correction.as_pulse_counts(pulses)

        assert pulse_count == pulses

    @pytest.mark.parametrize(
        "pulses",
        [
            (0, 0, 0, 0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0, 0),
            (-1, 0, 0, 0, 0, 0, 0),
        ],
    )
    def test_error(self, pulses: tuple[int, ...]) -> None:
        with pytest.raises(ValueError):
            error_correction.as_pulse_counts(pulses)


class TestAsPulseCounts:
    @pytest.mark.parametrize(
        "pulses",
        [
            (0, 0, 0, 0, 0, 0, 0),
            (10, 10, 10, 10, 10, 10, 10),
            (1, 2, 3, 4, 5, 6, 7),
        ],
    )
    def test_happy_path(self, pulses: tuple[int, ...]) -> None:
        pulse_count = error_correction.as_pulse_counts(pulses)

        assert pulse_count == pulses

    @pytest.mark.parametrize(
        "pulses",
        [
            (0, 0, 0, 0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0, 0),
            (-1, 0, 0, 0, 0, 0, 0),
        ],
    )
    def test_error(self, pulses: tuple[int, ...]) -> None:
        with pytest.raises(ValueError):
            error_correction.as_pulse_counts(pulses)


class TestAsPhoneNumber:
    @pytest.mark.parametrize(
        "value",
        [
            (0, 0, 0, 0, 0, 0, 0),
            "0000000",
            [0, 0, 0, 0, 0, 0, 0],
        ],
    )
    def test_happy_path(self, value: Union[str, Iterable[int]]) -> None:
        phone_number = error_correction.as_phone_number(value)

        assert phone_number == error_correction.PhoneNumber(
            (
                0,
                0,
                0,
                0,
                0,
                0,
                0,
            )
        )

    @pytest.mark.parametrize(
        "value",
        [
            "000000",
            "00000000",
            "aaaaaaa",
            (10, 0, 0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0, 0, 0, 0),
            (0, 0, 0, 0, 0, 0),
        ],
    )
    def test_error(self, value: Union[str, Iterable[int]]) -> None:
        with pytest.raises(ValueError):
            error_correction.as_phone_number(value)
