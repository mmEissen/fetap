import json
import time
from os import path
import filelock


class PhoneBookError(Exception): pass
class EntryExists(PhoneBookError): pass
class NumberExists(EntryExists): pass
class AddressExists(EntryExists): pass
class EntryDoesNotExist(PhoneBookError): pass
class NumberDoesNotExist(EntryDoesNotExist): pass
class AddressDoesNotExist(EntryDoesNotExist): pass


class PhoneBook:
    def __init__(self, file_path: str) -> None:
        self._numbers_to_addresses: dict[str, str] = {}
        self._addresses_to_numbers: dict[str, str] = {}
        self.last_loaded = 0
        self.file_path = file_path
        self._file_lock = filelock.FileLock(self.file_path + ".lock")
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        with self._file_lock:
            if not path.isfile(self.file_path):
                self._save_phone_book()

    def _save_phone_book(self) -> None:
        with open(self.file_path, "w") as f:
            json.dump(self._numbers_to_addresses, f, indent=2)
    
    def _maybe_reload_phone_book(self) -> None:
        if path.getmtime(self.file_path) < self.last_loaded:
            return
        self.last_loaded = time.time()
        with open(self.file_path) as f:
            self._numbers_to_addresses = json.load(f)
        self._addresses_to_numbers = {a: n for n, a in self._numbers_to_addresses.items()}

    def get_number(self, address: str, should_reload: bool=True) -> str:
        if should_reload:
            with self._file_lock:
                self._maybe_reload_phone_book()
        try:
            return self._addresses_to_numbers[address]
        except KeyError as e:
            raise NumberDoesNotExist() from e
    
    def get_address(self, number: str, should_reload: bool=True) -> str:
        if should_reload:
            with self._file_lock:
                self._maybe_reload_phone_book()
        try:
            return self._numbers_to_addresses[number]
        except KeyError as e:
            raise AddressDoesNotExist() from e

    def del_address(self, address: str) -> None:
        with self._file_lock:
            number = self._addresses_to_numbers.pop(address)
            del self._numbers_to_addresses[number]
            self._save_phone_book()
    
    def del_number(self, number: str) -> None:
        with self._file_lock:
            address = self._numbers_to_addresses.pop(number)
            del self._addresses_to_numbers[address]
            self._save_phone_book()

    def insert(self, number: str, address: str) -> None:
        with self._file_lock:
            self._maybe_reload_phone_book()
            try:
                self.get_address(address, should_reload=False)
            except AddressDoesNotExist:
                pass
            else:
                raise AddressExists()
            try:
                self.get_number(number, should_reload=False)
            except NumberDoesNotExist:
                pass
            else:
                raise NumberExists()
            self._numbers_to_addresses[number] = address
            self._addresses_to_numbers[address] = number
            self._save_phone_book()
    
    def list_all(self) -> list[tuple[str, str]]:
        with self._file_lock:
            self._maybe_reload_phone_book()
            return [(n, a) for n, a in sorted(self._numbers_to_addresses.items())]
