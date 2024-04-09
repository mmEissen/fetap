from __future__ import annotations
import contextlib
import dataclasses
import enum
import queue
import subprocess
import threading
from typing import Callable, Iterable
import requests
from os import path


DOWNLOAD_URL = (
    "https://github.com/mmEissen/pjsip-rpi-release/releases/download/v2.14.1/pjsua"
)
PJSUA_PATH = path.join(path.dirname(__file__), "pjsua")
_STDOUT_TIMEOUT = 10


def download_pjsua() -> None:
    with requests.get(DOWNLOAD_URL, stream=True) as response:
        response.raise_for_status()
        with open(PJSUA_PATH, "wb") as f:
            for chunk in response.iter_content():
                f.write(chunk)


def ensure_pjsua() -> None:
    if path.exists(PJSUA_PATH):
        return
    download_pjsua()


@contextlib.contextmanager
def run() -> Iterable[PJSua]:
    pjsua = PJSua()
    pjsua.start()
    try:
        yield pjsua
    finally:
        pjsua.stop()


class NotRunningError(Exception):
    pass


class ProcessDied(Exception):
    pass


class CallState(enum.Enum):
    IN_CALL = enum.auto()
    CALLING = enum.auto()
    INCOMING = enum.auto()
    IDLE = enum.auto()


class PJSua:
    def __init__(
        self,
        on_incoming_call: Callable[[], None],
        on_call_hangup: Callable[[], None],
        on_call_connected: Callable[[], None],
    ) -> None:
        self._on_incoming_call = on_incoming_call
        self._on_call_hangup = on_call_hangup
        self._on_call_connected = on_call_connected
        self._process_: subprocess.Popen | None = None
        self._supervisor_thread = threading.Thread(
            target=self._check_status_loop, daemon=True, name="pjsip-supervisor"
        )
        self._stdout_thread = threading.Thread(
            target=self._read_stdout_loop, daemon=True, name="pjsip-stdout"
        )
        self._command_queue: queue.Queue[tuple[str, float]] = queue.Queue()
        self._stdout_queue: queue.Queue[str] = queue.Queue()
        self._responses_queue: queue.Queue[str] = queue.Queue()
        self._should_stop = threading.Event()

        self._lock = threading.Lock()
        self._call_state = CallState.IDLE

    @property
    def call_state(self) -> CallState:
        with self._lock:
            return self._call_state

    @property
    def _process(self) -> subprocess.Popen:
        if self._process_ is None:
            raise NotRunningError()
        return self._process_

    def _check_status_loop(self):
        """pjsip-supervisor mainloop"""
        while not self._should_stop.is_set():
            if (returncode := self._process.poll()) is not None:
                raise ProcessDied(f"pjsua terminated unexpectedly: {returncode}")
            try:
                command, timeout = self._command_queue.get_nowait()
            except queue.Empty:
                pass
            else:
                self._process.stdin.write(command + "\n")
                self._process.stdin.flush()
                self._responses_queue.put_nowait(
                    self._stdout_queue.get(timeout=timeout)
                )
            self._check_calls()

    def _infer_call_state(self, call_list_response: str) -> CallState:
        current_call_lines = call_list_response.split("\n")[1:]

        if not current_call_lines:
            return CallState.IDLE
        if any(line.strip().endswith("[CONFIRMED]") for line in current_call_lines):
            return CallState.IN_CALL
        if any(line.strip().endswith("[CALLING]") for line in current_call_lines):
            return CallState.CALLING
        if any(line.strip().endswith("[INCOMING]") for line in current_call_lines):
            return CallState.INCOMING

    def _check_calls(self) -> None:
        """Runs on pjsip-supervisor"""
        self._process.stdin.write("call list\n")
        self._process.stdin.flush()
        response = self._stdout_queue.get(timeout=_STDOUT_TIMEOUT)

        new_state = self._infer_call_state(response)
        if new_state is self._call_state:
            return

        if new_state is CallState.INCOMING:
            self._on_incoming_call()
        if new_state is CallState.IN_CALL:
            self._on_call_connected()
        if self._call_state is CallState.IN_CALL:
            self._on_call_hangup()

        with self._lock:
            self._call_state = new_state

    def _read_stdout_loop(self):
        """pjsip-stdout mainloop"""
        buffer: list[str] = []
        while not self._should_stop.is_set():
            buffer.append(self._process.stdout.read(1))
            if "".join(buffer[-3:]) != ">>>":
                continue
            output = "".join(buffer[:-3]).strip()
            buffer = []
            self._stdout_queue.put_nowait(output)

    def start(self) -> None:
        assert self._process_ is None
        ensure_pjsua()
        self._process_ = subprocess.Popen(
            [
                "stdbuf",  # If we don't do this then there will appear to be no stdout
                "-o0",
                PJSUA_PATH,
                "--use-cli",
                "--max-calls=3",
                "--no-tones",
                "--no-color",
                "--log-level=0",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            # stderr=subprocess.DEVNULL,
            bufsize=0,
            universal_newlines=True,
        )
        self._supervisor_thread.start()
        self._stdout_thread.start()
        # When the process starts it prints the prompt symbols ">>>". We wan to
        # discard this first output
        self._stdout_queue.get(timeout=_STDOUT_TIMEOUT)

    def send_command(self, command: str, timeout=_STDOUT_TIMEOUT) -> str:
        self._command_queue.put_nowait((command, timeout))
        response = self._responses_queue.get(timeout=timeout)
        print(response)
        return response

    def call(self, address: str) -> None:
        self.send_command(f"call new sip:{address}")

    def accept_call(self) -> None:
        self.send_command("call answer 200")

    def call_list(self) -> None:
        response = self.send_command("call list")
        print(response)
        return self._infer_call_state(response)

    def hangup_all(self) -> None:
        self.send_command("call hangup_all")

    def stop(self) -> None:
        self._should_stop.set()
        self._process.terminate()


def test() -> PJSua:
    p = PJSua(lambda: None, lambda: None, lambda: None)
    p.start()
    return p
