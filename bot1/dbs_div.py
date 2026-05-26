import sqlite3 as sq
import asyncio
import env
import asyncpg

CREATE_USERS_SQL = """
CREATE TABLE IF NOT EXISTS users (
id SERIAL PRIMARY KEY,
tg_id BIGINT,
subjects VARCHAR(255),
class INT,
region INT
);
"""

MIGRATE_USERS_SQL = """
ALTER TABLE users
ALTER COLUMN subjects TYPE VARCHAR(255);
"""

MIGRATE_EVENTS_SQL = """
ALTER TABLE IF EXISTS events
ALTER COLUMN name_1 TYPE VARCHAR(100) USING LEFT(name_1, 100),
ALTER COLUMN lvl TYPE VARCHAR(100) USING LEFT(lvl, 100),
ALTER COLUMN frm TYPE VARCHAR(100) USING LEFT(frm, 100),
ALTER COLUMN subjects TYPE VARCHAR(255) USING LEFT(subjects, 255),
ALTER COLUMN description_1 TYPE VARCHAR(500) USING LEFT(description_1, 500);
"""

MIGRATE_EVENTS_LINK_SQL = """
ALTER TABLE IF EXISTS events
ALTER COLUMN lnk TYPE VARCHAR(100) USING LEFT(lnk, 100);
"""

MIGRATE_EVENTS_REGION_SQL = """
ALTER TABLE IF EXISTS events
ADD COLUMN IF NOT EXISTS region INT;
"""

CREATE_REGISTERED_EVENTS_SQL = """
CREATE TABLE IF NOT EXISTS registered_events (
id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
user_id BIGINT NOT NULL,
tg_id BIGINT NOT NULL,
event_id BIGINT NOT NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_REGISTERED_EVENTS_UNIQUE_SQL = """
CREATE UNIQUE INDEX IF NOT EXISTS idx_registered_events_user_event
ON registered_events (user_id, event_id);
"""

CREATE_SENT_NOTIFICATIONS_SQL = """
CREATE TABLE IF NOT EXISTS sent_notifications (
id SERIAL PRIMARY KEY,
tg_id BIGINT NOT NULL,
event_id INT NOT NULL,
notification_type VARCHAR(10) NOT NULL,
sent_at TIMESTAMP NOT NULL DEFAULT NOW(),
UNIQUE (tg_id, event_id, notification_type)
);
"""

INSERT_USER_SQL = """
INSERT INTO users (tg_id, subjects, class, region)
VALUES ($1, $2, $3, $4);
"""

UPDATE_USER_SQL = """
UPDATE users
SET subjects = $2, class = $3, region = $4
WHERE id = $1;
"""

GET_USER_SQL = """
SELECT id, tg_id, subjects, class, region
FROM users
WHERE tg_id = $1
ORDER BY id DESC
LIMIT 1;
"""

UPDATE_USER_SUBJECTS_SQL = """
UPDATE users
SET subjects = $2
WHERE id = $1;
"""

REGISTER_MATCHING_EVENTS_SQL = """
WITH latest_user AS (
    SELECT id, tg_id, subjects, class, region
    FROM users
    WHERE tg_id = $1
    ORDER BY id DESC
    LIMIT 1
)
INSERT INTO registered_events (user_id, tg_id, event_id)
SELECT u.id, u.tg_id, e.id
FROM latest_user u
JOIN events e
    ON e.class_start <= u.class
   AND e.class_end >= u.class
   AND (e.region IS NULL OR e.region = 0 OR e.region = u.region)
WHERE u.subjects IS NOT NULL
  AND length(u.subjects) >= 3
  AND EXISTS (
      SELECT 1
      FROM generate_series(1, length(u.subjects), 3) AS gs(pos)
      WHERE substring(lower(u.subjects) from pos for 3) <> ''
        AND strpos(
            lower(coalesce(e.subjects, '')),
            substring(lower(u.subjects) from pos for 3)
        ) > 0
  )
  AND NOT EXISTS (
      SELECT 1
      FROM registered_events re
      WHERE re.user_id = u.id
        AND re.event_id = e.id
  )
RETURNING event_id;
"""

DUE_NOTIFICATIONS_SQL = """
WITH due_types(notification_type, days_before) AS (
    VALUES ('month', 30), ('week', 7), ('day', 1)
)
SELECT DISTINCT ON (re.tg_id, e.id, due_types.notification_type)
    re.tg_id,
    u.subjects AS user_subjects,
    e.id AS event_id,
    e.name_1,
    e.subjects AS event_subjects,
    e.date_start,
    e.lnk,
    due_types.notification_type
FROM registered_events re
JOIN users u
    ON u.id = re.user_id
JOIN events e
    ON e.id = re.event_id
JOIN due_types
    ON e.date_start::date = CURRENT_DATE + due_types.days_before
WHERE u.subjects IS NOT NULL
  AND length(u.subjects) >= 3
  AND e.class_start <= u.class
  AND e.class_end >= u.class
  AND (e.region IS NULL OR e.region = 0 OR e.region = u.region)
  AND EXISTS (
      SELECT 1
      FROM generate_series(1, length(u.subjects), 3) AS gs(pos)
      WHERE substring(lower(u.subjects) from pos for 3) <> ''
        AND strpos(
            lower(coalesce(e.subjects, '')),
            substring(lower(u.subjects) from pos for 3)
        ) > 0
  )
  AND NOT EXISTS (
      SELECT 1
      FROM sent_notifications sn
      WHERE sn.tg_id = re.tg_id
        AND sn.event_id = e.id
        AND sn.notification_type = due_types.notification_type
  )
ORDER BY re.tg_id, e.id, due_types.notification_type, e.date_start ASC;
"""

MARK_NOTIFICATION_SENT_SQL = """
INSERT INTO sent_notifications (tg_id, event_id, notification_type)
VALUES ($1, $2, $3)
ON CONFLICT (tg_id, event_id, notification_type) DO NOTHING
RETURNING id;
"""


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

    async def ensure_users_table(self):
        await self.awrite(CREATE_USERS_SQL)
        await self.awrite(MIGRATE_USERS_SQL)

    async def ensure_schema(self):
        await self.ensure_users_table()
        await self.awrite(MIGRATE_EVENTS_SQL)
        await self.awrite(MIGRATE_EVENTS_LINK_SQL)
        await self.awrite(MIGRATE_EVENTS_REGION_SQL)
        await self.awrite(CREATE_REGISTERED_EVENTS_SQL)
        await self.awrite(CREATE_REGISTERED_EVENTS_UNIQUE_SQL)
        await self.awrite(CREATE_SENT_NOTIFICATIONS_SQL)

    async def aread(self,command:str  , *args):
        async with self.lock:
            return await self.conn.fetch(command , *args)
    async def awrite(self , commad:str , *args):
        async with self.lock:
            await self.conn.execute(commad , *args)
    async def save_user(self, tg_id:int, subjects:str, class_value:int, region:int):
        async with self.lock:
            row = await self.conn.fetchrow(GET_USER_SQL, tg_id)
            if row is None:
                await self.conn.execute(INSERT_USER_SQL, tg_id, subjects, class_value, region)
            else:
                await self.conn.execute(UPDATE_USER_SQL, row["id"], subjects, class_value, region)
            await self.conn.fetch(REGISTER_MATCHING_EVENTS_SQL, tg_id)

    async def get_user(self, tg_id:int):
        async with self.lock:
            return await self.conn.fetchrow(GET_USER_SQL, tg_id)

    async def update_user_subjects(self, tg_id:int, subjects:str):
        async with self.lock:
            row = await self.conn.fetchrow(GET_USER_SQL, tg_id)
            if row is None:
                return None
            await self.conn.execute(UPDATE_USER_SUBJECTS_SQL, row["id"], subjects)
            await self.conn.fetch(REGISTER_MATCHING_EVENTS_SQL, tg_id)
            return await self.conn.fetchrow(GET_USER_SQL, tg_id)

    async def register_matching_events(self, tg_id:int):
        async with self.lock:
            try:
                return await self.conn.fetch(REGISTER_MATCHING_EVENTS_SQL, tg_id)
            except asyncpg.UndefinedTableError:
                return []

    async def get_due_notifications(self):
        async with self.lock:
            try:
                return await self.conn.fetch(DUE_NOTIFICATIONS_SQL)
            except asyncpg.UndefinedTableError:
                return []

    async def mark_notification_sent(self, tg_id:int, event_id:int, notification_type:str) -> bool:
        async with self.lock:
            row = await self.conn.fetchrow(
                MARK_NOTIFICATION_SENT_SQL,
                tg_id,
                event_id,
                notification_type,
            )
            return row is not None
    async def close(self):
        if self.conn:
            await self.conn.close()
            self.conn = None

pg = pgdb(user= env.POSTGRES_USER , password=env.POSTGRES_PASSWORD , dbs=env.POSTGRES_DB , host="db")
