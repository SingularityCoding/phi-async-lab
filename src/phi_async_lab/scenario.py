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
    delay: float
    results: tuple[ResultTemplate, ...]


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
    return [
        SearchResult(
            source=source.name,
            title=template.title,
            snippet=f"{template.snippet} Query: {query}",
        )
        for template in source.results
    ]
