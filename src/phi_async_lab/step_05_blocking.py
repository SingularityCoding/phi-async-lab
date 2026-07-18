# Step 05：证明「async def」不会自动让函数体变得可抢占——
# 阻塞调用还是会冻结同一个 event loop 上的其他 Task。
import asyncio
import time
from collections.abc import Awaitable, Callable

from phi_async_lab.events import EventKind, EventLog

BLOCK_SECONDS = 0.12


async def blocking_search(event_log: EventLog) -> None:
    event_log.record("search", EventKind.STARTED, "blocking version")
    event_log.record("search", EventKind.WAITING, f"time.sleep({BLOCK_SECONDS:.2f})")
    # 故意用同步的 time.sleep()：即使外面套了 async def，这一行也不会把控制权交还
    # event loop，同一个 loop 上的 heartbeat 完全无法推进。
    time.sleep(BLOCK_SECONDS)
    event_log.record("search", EventKind.COMPLETED)


async def cooperative_search(event_log: EventLog) -> None:
    event_log.record("search", EventKind.STARTED, "cooperative version")
    event_log.record("search", EventKind.WAITING, f"asyncio.sleep({BLOCK_SECONDS:.2f})")
    # 换成 await asyncio.sleep()：这才是一个真正的挂起点，heartbeat 得以插入执行。
    await asyncio.sleep(BLOCK_SECONDS)
    event_log.record("search", EventKind.RESUMED)
    event_log.record("search", EventKind.COMPLETED)


async def heartbeat(event_log: EventLog) -> None:
    event_log.record("heartbeat", EventKind.STARTED)
    for number in range(1, 5):
        await asyncio.sleep(0.03)
        event_log.record("heartbeat", EventKind.TICK, str(number))
    event_log.record("heartbeat", EventKind.COMPLETED)


async def run_pair(operation: Callable[[EventLog], Awaitable[None]]) -> EventLog:
    event_log = EventLog()
    # search 和 heartbeat 是同一个 event loop 上的两个平级 Task，
    # 谁能推进完全取决于谁先让出控制权。
    async with asyncio.TaskGroup() as task_group:
        task_group.create_task(operation(event_log))
        task_group.create_task(heartbeat(event_log))
    return event_log


async def main() -> None:
    blocking_log = await run_pair(blocking_search)
    cooperative_log = await run_pair(cooperative_search)

    print("Step 05A - a blocking call freezes the event loop")
    print("================================================")
    print(blocking_log.render())
    print()
    print("Step 05B - an await lets the heartbeat run")
    print("=============================================")
    print(cooperative_log.render())


if __name__ == "__main__":
    asyncio.run(main())
