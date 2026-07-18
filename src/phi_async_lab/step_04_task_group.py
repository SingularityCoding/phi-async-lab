# Step 04：用 TaskGroup 表达「这些子任务属于谁、作用域结束时必须都已完成或清理」。
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
    tasks: list[asyncio.Task[list[SearchResult]]] = []

    # 进入 async with 就开启了一个「子任务所有权」作用域：
    # 正常离开这个作用域之前，TaskGroup 会等待组里所有 Task 完成；
    # 如果有任务失败或被取消，它也会负责取消并等待其余未完成的兄弟任务。
    async with asyncio.TaskGroup() as task_group:
        for source in sources:
            task = task_group.create_task(
                search(source, query, log),
                name=f"search:{source.name}",
            )
            tasks.append(task)

    # 走到这里，作用域已经退出，所有 Task 保证已经结束，读取 result() 是安全的。
    results = [result for task in tasks for result in task.result()]
    return results, log


async def main() -> None:
    started_at = time.perf_counter()
    results, event_log = await collect(QUERY)
    elapsed = time.perf_counter() - started_at
    print_report("Step 04 - structured concurrency", event_log, results, elapsed)


if __name__ == "__main__":
    asyncio.run(main())
