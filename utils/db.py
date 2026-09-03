import aiosqlite

DB_PATH = "masis.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS guilds (
                guild_id INTEGER PRIMARY KEY,
                provider TEXT,
                encrypted_api_key TEXT,
                language TEXT DEFAULT 'en'
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS faq_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keywords TEXT,
                answer_key TEXT
            )
        """)
        await db.commit()

async def get_guild(guild_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM guilds WHERE guild_id = ?", (guild_id,)
        )
        row = await cursor.fetchone()
        
        if not row:
            await db.execute(
                "INSERT INTO guilds (guild_id, language) VALUES (?, 'en')", (guild_id,)
            )
            await db.commit()
            cursor = await db.execute(
                "SELECT * FROM guilds WHERE guild_id = ?", (guild_id,)
            )
            row = await cursor.fetchone()
            
        return row

async def update_guild_api(guild_id: int, provider: str, encrypted_key: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO guilds (guild_id, provider, encrypted_api_key) 
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET 
                provider=excluded.provider, 
                encrypted_api_key=excluded.encrypted_api_key
            """, 
            (guild_id, provider, encrypted_key)
        )
        await db.commit()

async def update_guild_language(guild_id: int, language: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO guilds (guild_id, language) 
            VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET 
                language=excluded.language
            """, 
            (guild_id, language)
        )
        await db.commit()

async def get_all_faqs():
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM faq_entries")
        return await cursor.fetchall()

        cursor = await db.execute("SELECT COUNT(*) FROM faq_entries")
        count = (await cursor.fetchone())[0]
        if count == 0:
            initial_faqs = [
                ("api key anahtar al nasıl", "faq_api_key"),
                ("sağlayıcı provider openai gemini hangi destek", "faq_providers"),
                ("hata error geçersiz invalid çalışmıyor", "faq_errors")
            ]
            await db.executemany("INSERT INTO faq_entries (keywords, answer_key) VALUES (?, ?)", initial_faqs)
            await db.commit()