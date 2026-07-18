# 统一的输出格式，让每个 checkpoint 的 main() 都不用自己拼报告。
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
    print(f"elapsed: {elapsed:.2f}s")  # 仅供直观感受，判断对错请看 event_log 里的顺序
