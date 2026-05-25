import sqlite3 as sq
import asyncio
import env
import asyncpg
class Database:
    def __init__(self , db_name : str):
        self.conn = sq.connect(db_name)
        self.cur = self.conn.cursor()
        self.lock = asyncio.Lock() 

    async def aread(self, request: str):
        async with self.lock: 
            return self.cur.execute(request ).fetchall()
    # В классе Database (в твоем файле)
    async def awrite(self, request: str, params: tuple = ()):
        async with self.lock:
            self.cur.execute(request, params)
            self.conn.commit()
            return self.cur.lastrowid  # Возвращает ID последней вставки
    def read(self ,request : str):
        return self.cur.execute(request).fetchall()
    def write(self , request: str):
        self.cur.execute(request)
        self.conn.commit()
    def save(self):
        self.conn.commit()
    def close(self):
        self.conn.close()

# db = Database(env.db_file)
# try:
#     db.write("CREATE TABLE IF NOT EXISTS users(id INTEGER , registred INTEGER)") # 0 - нет , 1-  да , 2 -  в очереди на регистацию , 3  - забанен
# except:
#     print("[!]DB ERROR")



class pgdb:
    def __init__(self ,user , password , dbs , host , port = 5432):
        self.creds = {
            "user": user,
            "password": password,
            "database": dbs,
            "host": host,
            "port":port
        }
        self.conn = None
        self.lock = asyncio.Lock()
    async def connect(self):
        if not self.conn:
            self.conn = await asyncpg.connect(**self.creds)
        return self

    async def aread(self,command:str  , *args):
        async with self.lock:
            return await self.conn.fetch(command , *args)
    async def awrite(self , commad:str , *args):
        async with self.lock:
            await self.conn.execute(commad , *args)
    async def close(self):
        await self.conn.close()

pg = pgdb(user= env.POSTGRES_USER , password=env.POSTGRES_PASSWORD , dbs=env.POSTGRES_DB , host="db")

        