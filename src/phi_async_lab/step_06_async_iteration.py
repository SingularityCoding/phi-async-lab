# Step 06：用 async for 一边消费流式结果，一边让另一个 progress Task 继续推进。
import asyncio
from collections.abc import AsyncIterator

from phi_async_lab.events import EventKind, EventLog
from phi_async_lab.scenario import SOURCES, SearchResult, SourceSpec, materialize

QUERY = "How do I cancel async work safely?"
DOCS_SOURCE = SOURCES[0]


async def stream(
    source: SourceSpec,
    query: str,
    event_log: EventLog,
) -> AsyncIterator[SearchResult]:
    event_log.record(source.name, EventKind.STARTED, "stream")
    results = materialize(source, query)
    delay_per_result = source.delay / len(results)

    for result in results:
        event_log.record(source.name, EventKind.WAITING, result.title)
        # 每次 yield 前都会 await，这是一个真正的挂起点：
        # progress Task 正是趁这个空隙才有机会运行。
        await asyncio.sleep(delay_per_result)
        event_log.record(source.name, EventKind.RESUMED, result.title)
        # yield 把当前结果交给调用者，同时记住这里的执行位置，
        # 下次被 __anext__ 驱动时从这里继续。
        yield result

    event_log.record(source.name, EventKind.COMPLETED, f"{len(results)} chunks")


async def consume(
    source: SourceSpec,
    query: str,
    event_log: EventLog,
    finished: asyncio.Event,
) -> list[SearchResult]:
    results: list[SearchResult] = []
    try:
        # consume() 和 stream() 属于同一条调用链，不是两个并发 Task；
        # 真正独立的另一个 Task 是下面的 show_progress()。
        async for result in stream(source, query, event_log):
            results.append(result)
            event_log.record("consumer", EventKind.OBSERVED, result.title)
        return results
    finally:
        # 不管正常结束还是被打断，都要通知 progress 该停下来了。
        finished.set()


async def show_progress(finished: asyncio.Event, event_log: EventLog) -> None:
    event_log.record("progress", EventKind.STARTED)
    tick = 0
    while not finished.is_set():
        await asyncio.sleep(0.02)
        if not finished.is_set():
            tick += 1
            event_log.record("progress", EventKind.TICK, str(tick))
    event_log.record("progress", EventKind.COMPLETED)


async def run_streaming_demo(
    source: SourceSpec = DOCS_SOURCE,
    query: str = QUERY,
) -> tuple[list[SearchResult], EventLog]:
    event_log = EventLog()
    finished = asyncio.Event()

    async with asyncio.TaskGroup() as task_group:
        consumer_task = task_group.create_task(consume(source, query, event_log, finished))
        task_group.create_task(show_progress(finished, event_log))

    return consumer_task.result(), event_log


async def main() -> None:
    results, event_log = await run_streaming_demo()
    print("Step 06 - async iteration with progress")
    print("=======================================")
    print(event_log.render())
    print()
    print(f"results: {len(results)}")


if __name__ == "__main__":
    asyncio.run(main())
