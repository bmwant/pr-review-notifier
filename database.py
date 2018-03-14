import time

import attr
import aiopg

import config


@attr.s
class Review(object):
    id = attr.ib()
    count_value = attr.ib()
    waiting_from = attr.ib()
    issue_number = attr.ib()
    pr_name = attr.ib()
    pr_url = attr.ib()


async def insert_new_review(issue_number, pr_name, pr_url):
    async with aiopg.create_pool(config.DATABASE_URL, echo=True) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                date = int(time.time())
                query = (
                    'INSERT INTO reviews(waiting_from, issue_number, pr_name, '
                    'pr_url) VALUES(to_timestamp(%s), %s, %s, %s) '
                    'RETURNING id;'
                )
                await cur.execute(query, (date, issue_number, pr_name, pr_url))
                result = await cur.fetchone()
                return result[0]


async def get_review(review_id):
    async with aiopg.create_pool(config.DATABASE_URL) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                query = 'SELECT * FROM reviews WHERE id = %s;'
                await cur.execute(query, (review_id,))
                result = await cur.fetchone()
                if result is not None:
                    return Review(*result)


async def update_reviews_count(review_id):
    async with aiopg.create_pool(config.DATABASE_URL) as pool:
        async with pool.acquire() as conn:
            async with conn.cursor() as cur:
                update_query = (
                    'UPDATE reviews SET count_value = count_value + 1 '
                    'WHERE id = %s;'
                )
                await cur.execute(update_query, (review_id,))
                select_query = (
                    'SELECT count_value FROM reviews '
                    'WHERE id = %s;'
                )
                await cur.execute(select_query, (review_id,))
                result = await cur.fetchone()
                return result[0]
