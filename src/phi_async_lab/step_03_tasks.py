# Step 03：先把三个 coroutine 都包装成 Task 再等待，请求才真正开始交错推进。
import asyncio
import time
from collections.abc import Sequence

from phi_async_lab.events import EventKind, EventLog
from phi_async_lab.reporting import print_report
from phi_async_lab.scenario import SOURCES, SearchResult, SourceSpec, materialize

QUERY = "How do I cancel async work safely?"


async def search(source: SourceSpec, query: str, event_log: EventLog) -> list[SearchResult]:
    event_log.record(source.name, EventKind.STARTED, query)
    event_log.record(source.name, EventKind.WAITING, f"{source.delay:.2f}s")
    await asyncio.sleep(source.delay)
    event_log.record(source.name, EventKind.RESUMED)
    results = materialize(source, query)
    event_log.record(source.name, EventKind.COMPLETED, f"{len(results)} results")
    return results


async def collect(
    query: str,
    sources: Sequence[SourceSpec] = SOURCES,
    event_log: EventLog | None = None,
) -> tuple[list[SearchResult], EventLog]:
    log = event_log or EventLog()
    # 关键区别在这里：三个 Task 在进入等待循环之前就已经全部创建，
    # 也就是全部登记给了 event loop。
    tasks = [
        asyncio.create_task(search(source, query, log), name=f"search:{source.name}")
        for source in sources
    ]

    results: list[SearchResult] = []
    for task in tasks:
        # await 第一个 Task 时，另外两个已经登记的 Task 也能在同一个 event loop 上推进。
        # 结果仍按 tasks 列表顺序收集，但「完成顺序」由各自的等待时长决定。
        results.extend(await task)
    return results, log


async def main() -> None:
    started_at = time.perf_counter()
    results, event_log = await collect(QUERY)
    elapsed = time.perf_counter() - started_at
    print_report("Step 03 - explicit tasks", event_log, results, elapsed)


if __name__ == "__main__":
    asyncio.run(main())
