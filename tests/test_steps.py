import asyncio
from dataclasses import replace

from phi_async_lab.events import EventKind
from phi_async_lab.scenario import SOURCES
from phi_async_lab.step_01_sync import collect as collect_sync
from phi_async_lab.step_02_sequential_async import collect as collect_sequential_async
from phi_async_lab.step_03_tasks import collect as collect_with_tasks
from phi_async_lab.step_04_task_group import collect as collect_with_task_group
from phi_async_lab.step_05_blocking import (
    blocking_search,
    cooperative_search,
    run_pair,
)
from phi_async_lab.step_06_async_iteration import run_streaming_demo
from phi_async_lab.step_07_cancellation import (
    run_deadline_demo,
    run_explicit_cancel_demo,
)

QUERY = "test query"
FAST_SOURCES = tuple(replace(source, delay=0.01) for source in SOURCES)


def event_index(events: tuple, actor: str, kind: EventKind) -> int:
    return next(
        index for index, event in enumerate(events) if event.actor == actor and event.kind == kind
    )


def test_sync_collection_finishes_each_source_before_starting_the_next() -> None:
    results, event_log = collect_sync(QUERY, FAST_SOURCES)

    assert len(results) == 7
    for current, following in zip(FAST_SOURCES, FAST_SOURCES[1:], strict=False):
        assert event_index(event_log.events, current.name, EventKind.COMPLETED) < event_index(
            event_log.events, following.name, EventKind.STARTED
        )


async def test_sequential_awaits_still_finish_before_starting_the_next_source() -> None:
    results, event_log = await collect_sequential_async(QUERY, FAST_SOURCES)

    assert len(results) == 7
    for current, following in zip(FAST_SOURCES, FAST_SOURCES[1:], strict=False):
        assert event_index(event_log.events, current.name, EventKind.COMPLETED) < event_index(
            event_log.events, following.name, EventKind.STARTED
        )


async def test_explicit_tasks_start_every_source_before_any_source_completes() -> None:
    results, event_log = await collect_with_tasks(QUERY, FAST_SOURCES)

    assert len(results) == 7
    last_start = max(
        event_index(event_log.events, source.name, EventKind.STARTED) for source in FAST_SOURCES
    )
    first_completion = min(
        event_index(event_log.events, source.name, EventKind.COMPLETED) for source in FAST_SOURCES
    )
    assert last_start < first_completion


async def test_task_group_starts_every_source_and_preserves_result_order() -> None:
    results, event_log = await collect_with_task_group(QUERY, FAST_SOURCES)

    assert [result.source for result in results] == [
        source.name for source in FAST_SOURCES for _ in source.results
    ]
    last_start = max(
        event_index(event_log.events, source.name, EventKind.STARTED) for source in FAST_SOURCES
    )
    first_completion = min(
        event_index(event_log.events, source.name, EventKind.COMPLETED) for source in FAST_SOURCES
    )
    assert last_start < first_completion


async def test_blocking_call_prevents_heartbeat_from_starting() -> None:
    event_log = await run_pair(blocking_search)

    assert event_index(event_log.events, "search", EventKind.COMPLETED) < event_index(
        event_log.events, "heartbeat", EventKind.STARTED
    )


async def test_cooperative_wait_allows_heartbeat_to_start() -> None:
    event_log = await run_pair(cooperative_search)

    assert event_index(event_log.events, "heartbeat", EventKind.STARTED) < event_index(
        event_log.events, "search", EventKind.COMPLETED
    )


async def test_async_iterator_yields_results_while_progress_runs() -> None:
    source = replace(SOURCES[0], delay=0.06)
    results, event_log = await run_streaming_demo(source, QUERY)

    assert len(results) == len(source.results)
    assert any(
        event.actor == "progress" and event.kind == EventKind.TICK for event in event_log.events
    )
    observed = [
        event.detail
        for event in event_log.events
        if event.actor == "consumer" and event.kind == EventKind.OBSERVED
    ]
    assert observed == [result.title for result in results]


async def test_timeout_cleans_every_started_source() -> None:
    sources = tuple(replace(source, delay=0.10) for source in SOURCES)
    event_log = await run_deadline_demo(timeout_seconds=0.02, sources=sources)

    for source in sources:
        kinds = [event.kind for event in event_log.events if event.actor == source.name]
        assert EventKind.CANCELLED in kinds
        assert EventKind.CLEANED in kinds
    assert event_log.events[-1].kind == EventKind.TIMED_OUT


async def test_explicit_cancellation_is_observed_after_cleanup() -> None:
    source = replace(SOURCES[0], delay=0.10)
    event_log = await run_explicit_cancel_demo(source)

    kinds = [event.kind for event in event_log.events]
    assert kinds.index(EventKind.CANCELLED) < kinds.index(EventKind.CLEANED)
    assert kinds.index(EventKind.CLEANED) < kinds.index(EventKind.OBSERVED)
    assert not [task for task in asyncio.all_tasks() if task.get_name() == "search-to-cancel"]
