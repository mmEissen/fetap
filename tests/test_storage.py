import pathlib
import pytest
from fetap import storage


@pytest.fixture()
def phone_book_path(tmp_path: pathlib.Path) -> str:
    return str((tmp_path / "phone_book.json").resolve())


@pytest.fixture()
def empty_phone_book(phone_book_path: str) -> storage.PhoneBook:
    return storage.PhoneBook(phone_book_path)


@pytest.fixture()
def numbers_and_addresses() -> list[tuple[str, str]]:
    return [
        ("110", "0.0.0.0"),
        ("112", "0.0.0.1"),
    ]


@pytest.fixture()
def phone_book(
    empty_phone_book: storage.PhoneBook, numbers_and_addresses: list[tuple[str, str]]
) -> storage.PhoneBook:
    for number, address in numbers_and_addresses:
        empty_phone_book.insert(number, address)
    return empty_phone_book


class TestPhoneBook:
    def test_store_and_list(
        self,
        phone_book: storage.PhoneBook,
        numbers_and_addresses: list[tuple[str, str]],
    ) -> None:
        all_numbers = phone_book.list_all()

        assert all_numbers == sorted(numbers_and_addresses)

    def test_second_instance_has_same_data(
        self,
        phone_book: storage.PhoneBook,
        phone_book_path: str,
        numbers_and_addresses: list[tuple[str, str]],
    ) -> None:
        second_phone_book = storage.PhoneBook(phone_book_path)

        all_numbers = second_phone_book.list_all()

        assert all_numbers == sorted(numbers_and_addresses)

    def test_second_instance_sees_new_numbers(
        self,
        phone_book: storage.PhoneBook,
        phone_book_path: str,
        numbers_and_addresses: list[tuple[str, str]],
    ) -> None:
        second_phone_book = storage.PhoneBook(phone_book_path)
        phone_book.insert("113", "0.0.0.3")

        all_numbers = second_phone_book.list_all()

        assert all_numbers == sorted(numbers_and_addresses + [("113", "0.0.0.3")]) 

    def test_get_number(self, phone_book: storage.PhoneBook, numbers_and_addresses: list[tuple[str, str]]) -> None:
        number, address = numbers_and_addresses[0]
        
        retrieved_number = phone_book.get_number(address)

        assert retrieved_number == number


    def test_get_address(self, phone_book: storage.PhoneBook, numbers_and_addresses: list[tuple[str, str]]) -> None:
        number, address = numbers_and_addresses[0]
        
        retrieved_address = phone_book.get_address(number)

        assert retrieved_address == address
