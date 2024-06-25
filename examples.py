import asyncio

async def greet(name):
    print(f"Hello, {name}!")

async def main():
    loop = asyncio.get_event_loop()

    # Schedule the greet coroutine to run after 2 seconds
    loop.call_later(2, asyncio.create_task, greet("Alice"))

    print("Waiting for 2 seconds...")
    await asyncio.sleep(2)
    print("Done waiting.")

# Run the event loop
asyncio.run(main())
