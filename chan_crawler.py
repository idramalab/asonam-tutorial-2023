import faktory
import logging
from faktory import Worker
from chan_client import Client
from datetime import datetime, timedelta
import time
import psycopg2
from dotenv import load_dotenv
import os

# these three lines allow psycopg to insert a dict into
# a jsonb coloumn
from psycopg2.extras import Json
from psycopg2.extensions import register_adapter
register_adapter(dict, Json)

# load our .env file
load_dotenv()

DATABASE_URL = os.environ.get('DATABASE_URL')
FAKTORY_URL = os.environ.get('FAKTORY_URL')

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')

def thread_numbers_from_catalog(catalog):
    thread_numbers = set()

    for page in catalog:
        page_number = page["page"]
        logging.debug(f'Getting thread numbers in catalog page number {page_number}')
        
        # now let's get thread numbers
        for thread in page["threads"]:
            thread_number = thread["no"]
            logging.debug(f'Found thread {thread_number}')

            thread_numbers.add(thread_number)

    return thread_numbers

def find_dead_threads(old_thread_numbers, new_thread_numbers):
    dead_threads = old_thread_numbers.difference(new_thread_numbers)
    return dead_threads

def crawl_thread(board, thread_number):
    client = Client()
    thread = client.get_thread(board, thread_number)


    logging.info(f'/{board}/{thread_number}: {thread}')

    # We really want to have a connection pool!
    # check psycopg docs!!

    conn = psycopg2.connect(
        dsn=DATABASE_URL
    )

    cur = conn.cursor()

    # for each post that we have, we want to insert it into the db
    for post in thread["posts"]:
        post_number = post["no"]
        
        # we want to use named parameters; check psycopg2 docs.
        sql = "INSERT INTO posts (board, thread_number, post_number, data) VALUES (%s, %s, %s, %s) RETURNING id"
        
        cur.execute(sql, (board, thread_number, post_number, post))

        # _commit_ our transaction so that it's actually persisted
        # to the db
        conn.commit()

        # it's often useful to know the id of the newly inserted
        # row. This is so you can launch other jobs that might
        # do additional processing.
        # e.g., to classify the toxicity of a post
        db_id = cur.fetchone()[0]
        logging.info(f'Inserted DB id: {db_id}')

    # now we should clean up our db stuff
    cur.close()
    # again, we really want to be using a connection pool
    conn.close()


def crawl_catalog(board, old_thread_numbers=[]):
    # make a new 4chan client
    client = Client()

    catalog = client.get_catalog(board)
    
    # we have a current catalog
    # we need to figure out which threads died so we can collect them
    new_thread_numbers = thread_numbers_from_catalog(catalog)
    logging.info(f'catalog thread numbers: {new_thread_numbers}')

    # now we need to figure out which threads have died, and issue a crawl
    # job for them
    dead_thread_numbers = find_dead_threads(set(old_thread_numbers), new_thread_numbers)

    for dead_thread_number in dead_thread_numbers:
        # enqueue a new job to collect the dead thread number
        with faktory.connection(FAKTORY_URL) as client:
            client.queue("crawl-thread", args=(board, dead_thread_number), queue="crawl-threads", reserve_for=60)

    # now we need to schedule to crawl the catalog again in 5 minutes
    run_at = datetime.utcnow() + timedelta(minutes=5)
    run_at = run_at.isoformat()[:-7] + "Z"
    logging.info(f'scheduling a new catalog crawl to run at: {run_at}')
    
    with faktory.connection(FAKTORY_URL) as client:
        client.queue("crawl-catalog", args=(board,list(new_thread_numbers)), queue="crawl-catalogs", reserve_for=60, at=run_at)




if __name__ == "__main__":
    # NB: You can (and in certain circumstances probably should) increase concurrency level here.
    
    w = Worker(faktory=FAKTORY_URL, queues=["crawl-catalogs", "crawl-threads"], concurrency=10, use_threads=True)
    w.register("crawl-catalog", crawl_catalog)
    w.register("crawl-thread", crawl_thread)
    logging.info("running?")
    w.run()