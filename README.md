# Phi Async Lab

Phi Async Lab 是进入 [Phi](https://github.com/SingularityCoding/phi) 正课前的确定性异步编程
实验。它用一个离线的多源开发文档检索器，帮助已有 Python 经验的学习者建立进入 Phi 所需的
`async` / `await` 心智模型。

## 学习方式

每个 checkpoint 都是完整、可独立运行的程序。请先预测事件顺序，再运行代码，最后用对应的
测试验证行为不变量。完整中文教程与 Async Readiness Check 位于 Phi 课程网站。

## 环境准备

需要 Python 3.12、uv 和 Git：

```bash
git clone https://github.com/SingularityCoding/phi-async-lab.git
cd phi-async-lab
uv sync --locked
uv run pytest
```

运行各个 checkpoint：

```bash
uv run python -m phi_async_lab.step_01_sync
uv run python -m phi_async_lab.step_02_sequential_async
uv run python -m phi_async_lab.step_03_tasks
uv run python -m phi_async_lab.step_04_task_group
uv run python -m phi_async_lab.step_05_blocking
uv run python -m phi_async_lab.step_06_async_iteration
uv run python -m phi_async_lab.step_07_cancellation
```

## 能力边界

必修主线覆盖：

- coroutine、Task 与 event loop；
- 顺序等待与并发执行；
- `asyncio.create_task()` 与 `TaskGroup`；
- 阻塞 event loop 的同步调用；
- `async for`、`async with`、timeout、cancellation 与 cleanup；
- `asyncio.run()` 的入口所有权；
- 确定性的异步 pytest。

本 Lab 不依赖真实网络，也不教授 Textual、LLM API、Queue、多数据源流式合并或完整的
`asyncio` API。
