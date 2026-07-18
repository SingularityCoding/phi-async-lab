from dataclasses import dataclass, field
from enum import StrEnum


class EventKind(StrEnum):
    STARTED = "started"
    WAITING = "waiting"
    RESUMED = "resumed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    CLEANED = "cleaned"
    TICK = "tick"
    TIMED_OUT = "timed_out"
    OBSERVED = "observed"


@dataclass(frozen=True, slots=True)
class Event:
    sequence: int
    actor: str
    kind: EventKind
    detail: str = ""

    def render(self) -> str:
        suffix = f" | {self.detail}" if self.detail else ""
        return f"{self.sequence:02d} | {self.actor:<10} | {self.kind.value:<10}{suffix}"


@dataclass(slots=True)
class EventLog:
    _events: list[Event] = field(default_factory=list)

    def record(self, actor: str, kind: EventKind, detail: str = "") -> None:
        self._events.append(Event(len(self._events) + 1, actor, kind, detail))

    @property
    def events(self) -> tuple[Event, ...]:
        return tuple(self._events)

    def render(self) -> str:
        return "\n".join(event.render() for event in self._events)
