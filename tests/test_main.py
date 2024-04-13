from __future__ import annotations

import dataclasses
import queue
import statemachine
from fetap import main

import pytest


@dataclasses.dataclass
class FakeHardware:
    events: list[main.PhoneEvent]

    def __call__(self, event_queue: queue.Queue) -> FakeHardware:
        for event in self.events:
            event_queue.put_nowait(event)
        event_queue.put_nowait(self.on_queue_empty)
        self.event_queue = event_queue
        return self

    def on_queue_empty(self, phone: main.Phone) -> None:
        assert False, "Unexpected end of queue"



class TestApp:
    @pytest.fixture
    def events(self) -> list[main.PhoneEvent]:
        return []
    
    @pytest.fixture
    def hardware(self, events: list[main.PhoneEvent]) -> main.FakeHardware:
        return FakeHardware(events)
    
    @pytest.fixture
    def hardware(self) -> main.FakeHardware:
        return main.Phone()

    @pytest.fixture
    def app(self, hardware: main.FakeHardware) -> main.App:
        return main.App(_hardware_factory=hardware)

    @pytest.mark.parametrize(
        "events, final_state",
        [
            pytest.param(
                [],
                main.Phone.idle,
            ),
            pytest.param(
                [
                    main.Event.RECEIVER_UP,
                    main.Event.DIAL_ACTIVATE,
                    main.Event.DIAL_PULSE,
                ],
                main.Phone.dial_active,
            ),
        ],
    )
    def test_event_chains(
        self, app: main.App, hardware: FakeHardware, final_state: statemachine.State
    ) -> None:
        for _ in range(len(hardware.events)):
            app.handle_next_event()

        assert app.phone.current_state == final_state
