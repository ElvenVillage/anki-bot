import asyncpg
from typing import Callable, Awaitable, Dict, Any
from os import getenv
from aiogram import BaseMiddleware
from aiogram.types import Message

async def create_db_pool():
    return await asyncpg.create_pool(
        database=getenv("DB_NAME"),
        user=getenv("DB_USER"),
        password=getenv("DB_PASSWORD"),
        port=getenv("DB_PORT"),
        host="db"
    )


class DbPoolMiddleware(BaseMiddleware):
    def __init__(self, pool: asyncpg.pool.Pool):
        super().__init__()
        self.pool = pool

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any],
    ) -> Any:
        async with self.pool.acquire() as connection:
            data["conn"] = connection
            return await handler(event, data)