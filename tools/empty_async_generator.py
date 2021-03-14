def empty_async_generator(fn):
    async def inner(*args, **kwargs):
        await fn(*args, **kwargs)

        # No "yield from []" in async functions :(
        return
        yield

    return inner
