from collections.abc import Sequence

from phi_async_lab.events import EventLog
from phi_async_lab.scenario import SearchResult


def print_report(
    title: str,
    event_log: EventLog,
    results: Sequence[SearchResult],
    elapsed: float,
) -> None:
    print(title)
    print("=" * len(title))
    print(event_log.render())
    print()
    print(f"results: {len(results)}")
    print(f"elapsed: {elapsed:.2f}s")
