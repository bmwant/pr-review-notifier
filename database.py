import time
from functools import partial

import aioodbc

import config
from utils import logger


connect = partial(aioodbc.connect, dsn=config.DSN, echo=True, autocommit=True)


async def insert_new_review(pr_id, pr_name, pr_url):
    async with connect() as conn:
        async with conn.cursor() as cur:
            date = int(time.time())
            query_tmpl = (
                'INSERT INTO reviews(waiting_from, pr_id, pr_name, pr_url) '
                'VALUES({waiting_from}, {pr_id}, "{pr_name}", "{pr_url}");'
            )
            query = query_tmpl.format(
                waiting_from=date,
                pr_id=pr_id,
                pr_name=pr_name,
                pr_url=pr_url,
            )
            logger.debug('Executing query %s', query)
            await cur.execute(query)
            await cur.execute('SELECT last_insert_rowid();')
            result = await cur.fetchone()
            return result[0]


async def get_review(review_id):
    async with connect() as conn:
        async with conn.cursor() as cur:
            query = 'SELECT * FROM reviews WHERE id = {review_id};'.format(
                review_id=review_id
            )
            await cur.execute(query)
            return await cur.fetchone()


async def update_reviews_count(review_id):
    async with connect() as conn:
        async with conn.cursor() as cur:
            update_query = (
                'UPDATE reviews SET count_num = count_num + 1 '
                'WHERE id = {review_id};'.format(review_id=review_id))
            await cur.execute(update_query)
            select_query = (
                'SELECT count_num FROM reviews '
                'WHERE id = {review_id};'.format(review_id=review_id))
            await cur.execute(select_query)
            result = await cur.fetchone()
            return result[0]
