# Step 02：加上了 async/await，但还没有并发——这一步专门用来打破
# 「函数标了 async 就会自动并发」这个常见误解。
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
    # 换成 await asyncio.sleep()：这里会把控制权交还 event loop，
    # 但此刻还没有其他 Task 存在，所以没人能利用这段空隙。
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
    results: list[SearchResult] = []
    # 依旧是顺序 await：本次 search() 完整返回后，下一次循环才会调用下一个 search()。
    for source in sources:
        results.extend(await search(source, query, log))
    return results, log


async def main() -> None:
    started_at = time.perf_counter()
    results, event_log = await collect(QUERY)
    elapsed = time.perf_counter() - started_at
    print_report("Step 02 - async but sequential", event_log, results, elapsed)


if __name__ == "__main__":
    # 只有最外层、还没有 event loop 的入口才调用 asyncio.run()。
    asyncio.run(main())
