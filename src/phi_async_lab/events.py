# 整个 Lab 用同一套「事件日志」记录发生了什么、以及发生的先后顺序。
# 墙钟时间（秒数）只用来建立直觉，真正稳定、可断言的是这里的事件序号和顺序。
from dataclasses import dataclass, field
from enum import StrEnum


class EventKind(StrEnum):
    STARTED = "started"  # 一段工作开始
    WAITING = "waiting"  # 即将进入等待（例如 await 一个 sleep 或 I/O）
    RESUMED = "resumed"  # 等待结束，代码从挂起点恢复执行
    COMPLETED = "completed"  # 工作正常完成
    CANCELLED = "cancelled"  # 收到取消信号（CancelledError）
    CLEANED = "cleaned"  # finally 块完成清理
    TICK = "tick"  # 后台任务（如心跳/进度）的一次周期性输出
    TIMED_OUT = "timed_out"  # 调用者观察到超时
    OBSERVED = "observed"  # 调用者观察到某个结果或异常


@dataclass(frozen=True, slots=True)
class Event:
    sequence: int  # 逻辑发生顺序，不是时间戳——多次运行的耗时会变，顺序不会
    actor: str  # 谁产生了这个事件（某个数据源、caller、heartbeat 等）
    kind: EventKind
    detail: str = ""

    def render(self) -> str:
        suffix = f" | {self.detail}" if self.detail else ""
        return f"{self.sequence:02d} | {self.actor:<10} | {self.kind.value:<10}{suffix}"


@dataclass(slots=True)
class EventLog:
    _events: list[Event] = field(default_factory=list)

    def record(self, actor: str, kind: EventKind, detail: str = "") -> None:
        # 序号按 record() 被调用的顺序自增，因此它反映的是「谁先让出/拿回控制权」，
        # 而不是「谁先被写在代码里」。
        self._events.append(Event(len(self._events) + 1, actor, kind, detail))

    @property
    def events(self) -> tuple[Event, ...]:
        return tuple(self._events)

    def render(self) -> str:
        return "\n".join(event.render() for event in self._events)
