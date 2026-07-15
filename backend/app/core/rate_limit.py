import asyncio

import anthropic
from google import genai
from openai import AsyncOpenAI

from app.core.config import settings

providers = {
    "anthropic": (5, 5),
    "openai": (5, 5),
    "deepseek": (5, 5),
    "gemini": (5, 5),
}

class TokenBucket:
    def __init__(self, refilltime: int, capacity: int):
        self.refilltime = refilltime
        self.capacity = capacity
        self.queue: asyncio.Queue[asyncio.Future] = asyncio.Queue()
        self.token = capacity
        self.started = False
        self.refill_broken = False
        self.refill_retry = 0

    async def refill_token(self):
        while True:
            if self.refill_broken:
                await asyncio.sleep(60)
            try:
                await asyncio.sleep(self.refilltime)
                if self.queue.empty():
                    if self.token < self.capacity:
                        self.token += 1
                else:
                    a = await self.queue.get()
                    a.set_result(None)
                self.refill_broken = False
                self.refill_retry = 0
            except Exception:
                print('error: failed to refill token')
                self.refill_retry += 1
                if self.refill_retry >= 5:
                    self.refill_broken = True
                    while not self.queue.empty():
                        a = await self.queue.get()
                        a.set_exception(RuntimeError('the token refill loop failed'))

    async def acquire(self):
        if self.refill_broken:
            raise RuntimeError('the token refill loop failed')
        if self.token > 0:
            self.token -= 1
            return True
        fut = asyncio.get_event_loop().create_future()
        await self.queue.put(fut)
        await fut
        return True
    
    def start(self):
        if not self.started:
            self.started = True
            asyncio.create_task(self.refill_token())

class LlmBackup:
    llm_order = ['openai', 'anthropic', 'deepseek', 'gemini']

    def __init__(self, provider) -> None:
        self.count = 0
        self.provider = provider

    async def retest(self):
        while True:
            match self.provider:
                case 'openai':
                    try:
                        client = AsyncOpenAI()
                        response = await client.chat.completions.create(
                            model="gpt-4",
                            messages=[{"role": "user", "content": "test, only give one sentence"}],
                        )
                        self.count = 0
                        break
                    except Exception:
                        await asyncio.sleep(60)
                case 'anthropic':
                    try:
                        client = anthropic.AsyncAnthropic()
                        message = await client.messages.create(
                            model="claude-opus-4-8",
                            max_tokens=1000,
                            messages=[{"role": "user", "content": "test, only give one sentence"}],
                        )
                        self.count = 0
                        break
                    except Exception:
                        await asyncio.sleep(60)
                case 'deepseek':
                    try:
                        client = AsyncOpenAI(
                            api_key=settings.deepseek_api_key,
                            base_url="https://api.deepseek.com",
                        )
                        response = await client.chat.completions.create(
                            model="deepseek-v4-pro",
                            messages=[{"role": "user", "content": "test, only give one sentence"}],
                        )
                        self.count = 0
                        break
                    except Exception:
                        await asyncio.sleep(60)
                case 'gemini':
                    try:
                        client = genai.Client()
                        response = await client.aio.models.generate_content(
                            model="gemini-3.1-pro",
                            contents="test, only give one sentence",
                        )
                        self.count = 0
                        break
                    except Exception:
                        await asyncio.sleep(60)
            
token_bucket = {provider: TokenBucket(refilltime, capacity) for provider, (refilltime, capacity) in providers.items()}
llm_backup = {provider: LlmBackup(provider) for provider in providers.keys()}