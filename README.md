# Phi Async Lab

如果你已经会写 Python，但 `async` / `await`、Task、event loop 这些概念在你脑子里还是一团
雾——这个 Lab 就是为你准备的。在正式进入 [Phi](https://github.com/SingularityCoding/phi)
课程之前，花 2–3 小时把这团雾理清楚，会让你后面轻松很多。

整个练习围绕一个离线的「多源文档检索」场景展开：所有数据都是本地固定的，不需要联网，也
不需要担心结果不稳定。

## 怎么学

Lab 拆成一个个 checkpoint，每一个都是完整、可以独立运行的小程序。建议按这个节奏走：

1. 先自己预测一下：这段代码运行起来，事件会按什么顺序发生？
2. 运行代码，看看和你的预测是否一致；
3. 跑一下对应的测试，确认你抓住的是真正稳定的行为，而不是巧合。

完整的中文教程和 Async Readiness Check（自测清单）都放在
[Phi 课程网站](https://singularitycoding.github.io/phi/prework/async-lab/) 上，跟着页面顺序
走会更顺畅。

## 开始之前

你需要准备好 Python 3.12、uv 和 Git：

```bash
git clone https://github.com/SingularityCoding/phi-async-lab.git
cd phi-async-lab
uv sync --locked
uv run pytest
```

想单独运行某一个 checkpoint，用下面对应的命令即可：

```bash
uv run python -m phi_async_lab.step_01_sync
uv run python -m phi_async_lab.step_02_sequential_async
uv run python -m phi_async_lab.step_03_tasks
uv run python -m phi_async_lab.step_04_task_group
uv run python -m phi_async_lab.step_05_blocking
uv run python -m phi_async_lab.step_06_async_iteration
uv run python -m phi_async_lab.step_07_cancellation
```

## 这个 Lab 教什么、不教什么

学完主线部分，你应该能够：

- 区分 coroutine、Task 与 event loop；
- 判断一段代码到底是顺序等待，还是并发执行；
- 用 `asyncio.create_task()` 和 `TaskGroup` 组织并发任务；
- 一眼看出哪些同步调用会把 event loop 卡住；
- 读懂 `async for`、`async with`、timeout、cancellation 与 cleanup；
- 知道 `asyncio.run()` 应该由谁来调用；
- 看懂并写出确定性的异步 pytest。

这个 Lab 不追求覆盖整个 `asyncio`：真实网络请求、Textual、LLM API、Queue、多数据源流式
合并这些内容都不在这次的范围里，留到你真正用到的时候再学也不迟。
