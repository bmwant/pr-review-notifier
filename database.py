import time
import aioodbc
import config


async def insert_new_review(pr_id, pr_name, pr_url):
    conn = await aioodbc.connect(dsn=config.DSN)
    cur = await conn.cursor()
    date = int(time.time())
    await cur.execute(
        'INSERT INTO reviews(waiting_from, pr_id, pr_name, pr_url) '
        'VALUES (?, ?, ?, ?)',
        (date, pr_id, pr_name, pr_url)
    )
    await cur.execute('SELECT last_insert_rowid();')
    result = await cur.fetchone()
    print(result)
    await cur.close()
    await conn.close()
    return 15


async def get_review(review_id):
    conn = await aioodbc.connect(dsn=config.DSN)
    cur = await conn.cursor()
    await cur.execute('SELECT * FROM reviews WHERE id = ?;', (review_id,))
    result = await cur.fetchone()
    print(result)
    await cur.close()
    await conn.close()
    return {'redirect_url': 'http://google.com'}
