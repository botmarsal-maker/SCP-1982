import asyncio
from contextvars import ContextVar

var = ContextVar("var", default="default")

async def background_task():
    print("Task start:", var.get())
    await asyncio.sleep(1)
    print("Task end:", var.get())

async def handler():
    token = var.set("modified")
    print("Handler start:", var.get())
    asyncio.create_task(background_task())
    print("Handler resetting")
    var.reset(token)
    print("Handler exit:", var.get())

async def main():
    await handler()
    await asyncio.sleep(2)

asyncio.run(main())
