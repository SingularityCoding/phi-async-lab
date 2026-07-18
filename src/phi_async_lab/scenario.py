# 所有 checkpoint 共用同一个「多源检索」场景和同一份固定数据，
# 这样每一页文档改变的只有并发控制流本身，而不是业务逻辑。
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SearchResult:
    source: str
    title: str
    snippet: str


@dataclass(frozen=True, slots=True)
class ResultTemplate:
    title: str
    snippet: str


@dataclass(frozen=True, slots=True)
class SourceSpec:
    name: str
    delay: float  # 模拟这个数据源的响应耗时，只用于制造可观察的等待
    results: tuple[ResultTemplate, ...]


# 三个数据源的延迟故意拉开差距（0.12 / 0.08 / 0.04 秒），
# 这样顺序等待与并发等待的耗时差异在肉眼和测试里都足够明显。
SOURCES = (
    SourceSpec(
        name="docs",
        delay=0.12,
        results=(
            ResultTemplate("Coroutines and Tasks", "Tasks drive coroutines on an event loop."),
            ResultTemplate("Task Cancellation", "Cancellation is observed at an await point."),
            ResultTemplate("Asynchronous Iterators", "async for consumes values over time."),
        ),
    ),
    SourceSpec(
        name="issues",
        delay=0.08,
        results=(
            ResultTemplate("Progress freezes during search", "A blocking call stopped the loop."),
            ResultTemplate("Cancelled search leaked work", "A child task was never awaited."),
        ),
    ),
    SourceSpec(
        name="notes",
        delay=0.04,
        results=(
            ResultTemplate("await is not concurrency", "Sequential awaits still run in order."),
            ResultTemplate("One owner for the loop", "Call asyncio.run only at the outer edge."),
        ),
    ),
)


def materialize(source: SourceSpec, query: str) -> list[SearchResult]:
    # 这是一个普通同步函数：生成结果本身不涉及等待，
    # 「等待」这件事总是由调用它的 checkpoint 代码显式表达（sleep / await sleep）。
    return [
        SearchResult(
            source=source.name,
            title=template.title,
            snippet=f"{template.snippet} Query: {query}",
        )
        for template in source.results
    ]
