import sqlalchemy as sa

meta = sa.MetaData()


review = sa.Table(
    'review', meta,
    sa.Column('id', sa.Integer, nullable=False, autoincrement=True),
    sa.Column('count', sa.Integer, default=0),
    sa.Column('waiting_from', sa.Date, nullable=False),
    sa.Column('pr_id', sa.Integer, nullable=False),
    sa.Column('pr_name', sa.String, nullable=False),
    sa.Column('pr_url', sa.String, nullable=False),

    # Indexes #
    sa.PrimaryKeyConstraint('id', name='review_id_pkey'),
)


async def init_database(app):
    conf = app['config']['postgres']
    engine = await aiopg.sa.create_engine(
        database=conf['database'],
        user=conf['user'],
        password=conf['password'],
        host=conf['host'],
        port=conf['port'],
        minsize=conf['minsize'],
        maxsize=conf['maxsize'],
        loop=app.loop)
    app['db'] = engine


import asyncio
import aioodbc


loop = asyncio.get_event_loop()


async def insert_new_review():
    pass


async def test_example():
    dsn = 'Driver=SQLite;Database=database.db'
    conn = await aioodbc.connect(dsn=dsn, loop=loop)

    cur = await conn.cursor()
    await cur.execute("SELECT 42 AS age;")
    rows = await cur.fetchall()
    print(rows)
    print(rows[0])
    print(rows[0].age)
    await cur.close()
    await conn.close()
