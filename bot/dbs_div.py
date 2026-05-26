import asyncio
import asyncpg
import env

class pgdb:
    def __init__(self, user, password, dbs, host, port=5432):
        self.creds = {
            "user": user,
            "password": password,
            "database": dbs,
            "host": host,
            "port": port
        }
        self.conn = None
        self.lock = asyncio.Lock()

    async def connect(self):
        if not self.conn:
            self.conn = await asyncpg.connect(**self.creds)
        return self

    async def aread(self, command: str, *args):
        async with self.lock:
            return await self.conn.fetch(command, *args)

    async def awrite(self, command: str, *args):
        async with self.lock:
            await self.conn.execute(command, *args)

    async def close(self):
        await self.conn.close()

pg = pgdb(user=env.POSTGRES_USER, password=env.POSTGRES_PASSWORD, dbs=env.POSTGRES_DB, host="db")
