# Step 07：取消是一个请求，不是瞬间终止——必须等待被取消的 Task 完成清理，
# 并让调用者观察到真实的终止状态。
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
        # 只记录，然后必须 re-raise：吞掉 CancelledError 会让调用者误以为任务正常完成。
        event_log.record(source.name, EventKind.CANCELLED)
        raise
    finally:
        # 无论正常完成、异常还是被取消，finally 都会执行，适合在这里释放资源。
        event_log.record(source.name, EventKind.CLEANED)


async def collect_with_deadline(
    query: str,
    timeout_seconds: float,
    sources: Sequence[SourceSpec] = SOURCES,
    event_log: EventLog | None = None,
) -> tuple[list[SearchResult], EventLog]:
    log = event_log or EventLog()
    tasks: list[asyncio.Task[list[SearchResult]]] = []

    # asyncio.timeout() 到期时通过 cancellation 中断当前等待；
    # 嵌套的 TaskGroup 会取消并等待尚未完成的子任务，退出后调用者看到 TimeoutError。
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
    # cancel() 只是发出请求，Task 要到下一个可挂起点才会真正观察到 CancelledError。
    task.cancel()
    try:
        # 调用者必须继续 await task，才能等到 cleanup 完成并观察到真实的终止状态。
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
