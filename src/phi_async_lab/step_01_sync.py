# Step 01：同步基线。没有 async，也没有并发——三个数据源严格排队执行。
import time
from collections.abc import Sequence

from phi_async_lab.events import EventKind, EventLog
from phi_async_lab.reporting import print_report
from phi_async_lab.scenario import SOURCES, SearchResult, SourceSpec, materialize

QUERY = "How do I cancel async work safely?"


def search(source: SourceSpec, query: str, event_log: EventLog) -> list[SearchResult]:
    event_log.record(source.name, EventKind.STARTED, query)
    event_log.record(source.name, EventKind.WAITING, f"{source.delay:.2f}s")
    # time.sleep() 是阻塞调用：线程原地等待，没有把控制权让给任何人。
    time.sleep(source.delay)
    event_log.record(source.name, EventKind.RESUMED)
    results = materialize(source, query)
    event_log.record(source.name, EventKind.COMPLETED, f"{len(results)} results")
    return results


def collect(
    query: str,
    sources: Sequence[SourceSpec] = SOURCES,
    event_log: EventLog | None = None,
) -> tuple[list[SearchResult], EventLog]:
    log = event_log or EventLog()
    results: list[SearchResult] = []
    # 普通 for 循环 + 普通函数调用：下一个 search() 必须等上一个完整返回才会开始。
    for source in sources:
        results.extend(search(source, query, log))
    return results, log


def main() -> None:
    started_at = time.perf_counter()
    results, event_log = collect(QUERY)
    elapsed = time.perf_counter() - started_at
    print_report("Step 01 - synchronous baseline", event_log, results, elapsed)


if __name__ == "__main__":
    main()
