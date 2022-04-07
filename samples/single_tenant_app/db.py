from databases import Database

database = Database("sqlite:///single_tenant_db.sqlite3")


async def create_tables():
    query = """CREATE TABLE IF NOT EXISTS configuration (
        id INTEGER PRIMARY KEY,
        auth_token VARCHAR(255),
        webhook_id VARCHAR(255),
        webhook_secret VARCHAR(255),
        saleor_jwks TEXT
    )"""
    await database.execute(query=query)


async def retrieve_app_data():
    query = "SELECT * FROM configuration"
    return await database.fetch_one(query=query)


async def create_app_data(
    auth_token: str, webhook_id: str, webhook_secret: str, saleor_jwks: str
):
    query = """INSERT INTO configuration (
        auth_token,
        webhook_id,
        webhook_secret,
        saleor_jwks
    ) VALUES (
        :auth_token,
        :webhook_id,
        :webhook_secret,
        :saleor_jwks
    )"""
    await database.execute(
        query=query,
        values={
            "auth_token": auth_token,
            "webhook_id": webhook_id,
            "webhook_secret": webhook_secret,
            "saleor_jwks": saleor_jwks,
        },
    )


async def update_app_data(
    id_: int, auth_token: str, webhook_id: str, webhook_secret: str, saleor_jwks: str
):
    query = """UPDATE configuration SET 
        auth_token = :auth_token,
        webhook_id = :webhook_id,
        webhook_secret = :webhook_secret,
        saleor_jwks = :saleor_jwks
    WHERE id = :id"""
    await database.execute(
        query=query,
        values={
            "id": id_,
            "auth_token": auth_token,
            "webhook_id": webhook_id,
            "webhook_secret": webhook_secret,
            "saleor_jwks": saleor_jwks,
        },
    )


async def upsert_app_data(
    auth_token: str, webhook_id: str, webhook_secret: str, saleor_jwks: str
):
    app_data = await retrieve_app_data()
    if not app_data:
        await create_app_data(
            auth_token=auth_token,
            webhook_id=webhook_id,
            webhook_secret=webhook_secret,
            saleor_jwks=saleor_jwks,
        )
    else:
        await update_app_data(
            id_=app_data["id"],
            auth_token=auth_token,
            webhook_id=webhook_id,
            webhook_secret=webhook_secret,
            saleor_jwks=saleor_jwks,
        )
