from inteliver.database.postgres import SessionLocal


async def get_db():
    async with SessionLocal() as db:
        yield db
