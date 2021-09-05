import heapq
import time
from collections import deque


class Awaitable:
    def __await__(self):
        yield


def switch():
    return Awaitable()


class Scheduler:
    def __init__(self):
        self.ready = deque()
        self.sleeping = []
        self.current = None  # Currently executing generator
        self.sequence = 0

    async def sleep(self, delay):
        # Current coroutine wants to sleep
        deadline = time.time() + delay
        self.sequence += 1
        heapq.heappush(self.sleeping, (deadline, self.sequence, self.current))
        self.current = None
        await switch()

    def new_task(self, coro):
        self.ready.append(coro)

    def run(self):
        while self.ready or self.sleeping:
            if not self.ready:
                deadline, _, coro = heapq.heappop(self.sleeping)
                delta = deadline - time.time()
                if delta > 0:
                    time.sleep(delta)
                self.ready.append(coro)
            try:
                self.current = self.ready.popleft()
                # Drive as a generator
                self.current.send(None)  # Send a value to a coroutine
                if self.current:
                    self.ready.append(self.current)
            except StopIteration:
                pass


class Task:
    def __init__(self, coro):
        self.coro = coro

    def __call__(self, *args, **kwargs):
        try:
            sched.current = self
            self.coro.send(None)
            if sched.current:
                sched.ready.append(self)
        except StopIteration:
            pass


sched = Scheduler()


async def countdown(n: int):
    while n > 0:
        print(f"Down {n}")
        # time.sleep(1)  # Blocking call (nothing else can run)
        await sched.sleep(4)
        # yield
        # await switch()  # Switch task
        n -= 1


async def countup(stop: int):
    x = 0
    while x < stop:
        print(f"Up {x}")
        # time.sleep(1)
        await sched.sleep(1)
        # yield
        # await switch()  # Switch task
        x += 1


if __name__ == "__main__":
    sched.new_task(countdown(5))
    sched.new_task(countup(20))
    sched.run()
