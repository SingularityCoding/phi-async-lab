import asyncio
from collections.abc import Sequence

from phi_async_lab.events import EventKind, EventLog
from phi_async_lab.scenario import SOURCES, SearchResult, SourceSpec, materialize

QUERY = "How do I cancel async work safely?"


async def search(source: SourceSpec, query: str, event_log: EventLog) -> list[SearchResult]:
    event_log.record(source.name, EventKind.STARTED)
    try:
        event_log.record(source.name, EventKind.WAITING, f"{source.delay:.2f}s")
        await asyncio.sleep(source.delay)
        event_log.record(source.name, EventKind.RESUMED)
        results = materialize(source, query)
        event_log.record(source.name, EventKind.COMPLETED, f"{len(results)} results")
        return results
    except asyncio.CancelledError:
        event_log.record(source.name, EventKind.CANCELLED)
        raise
    finally:
        event_log.record(source.name, EventKind.CLEANED)


async def collect_with_deadline(
    query: str,
    timeout_seconds: float,
    sources: Sequence[SourceSpec] = SOURCES,
    event_log: EventLog | None = None,
) -> tuple[list[SearchResult], EventLog]:
    log = event_log or EventLog()
    tasks: list[asyncio.Task[list[SearchResult]]] = []

    async with asyncio.timeout(timeout_seconds):
        async with asyncio.TaskGroup() as task_group:
            for source in sources:
                tasks.append(task_group.create_task(search(source, query, log)))

    results = [result for task in tasks for result in task.result()]
    return results, log


async def run_deadline_demo(
    timeout_seconds: float = 0.06,
    sources: Sequence[SourceSpec] = SOURCES,
) -> EventLog:
    event_log = EventLog()
    try:
        await collect_with_deadline(QUERY, timeout_seconds, sources, event_log)
    except TimeoutError:
        event_log.record("caller", EventKind.TIMED_OUT)
    return event_log


async def run_explicit_cancel_demo(source: SourceSpec = SOURCES[0]) -> EventLog:
    event_log = EventLog()
    task = asyncio.create_task(search(source, QUERY, event_log), name="search-to-cancel")

    await asyncio.sleep(0.02)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        event_log.record("caller", EventKind.OBSERVED, "CancelledError")

    return event_log


async def main() -> None:
    deadline_log = await run_deadline_demo()
    cancel_log = await run_explicit_cancel_demo()

    print("Step 07A - timeout cancels unfinished children")
    print("================================================")
    print(deadline_log.render())
    print()
    print("Step 07B - cancel is a request that must be awaited")
    print("====================================================")
    print(cancel_log.render())


if __name__ == "__main__":
    asyncio.run(main())
