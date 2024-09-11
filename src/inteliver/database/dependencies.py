from inteliver.database.postgres import SessionLocal


async def get_db():  # pragma: no cover
    async with SessionLocal() as db:
        yield db
