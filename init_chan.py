import logging
import time
import faktory
import chan_client
from datetime import datetime, timedelta
from faktory import Worker
from dotenv import load_dotenv
import os

logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',
                    level=logging.DEBUG,
                    datefmt='%Y-%m-%d %H:%M:%S')

load_dotenv()
# I believe that the faktory client might automatically use this environment
# variable if no connection information is provided; you should check docs.
FAKTORY_URL = os.environ.get('FAKTORY_URL')

with faktory.connection(faktory=FAKTORY_URL) as client:

    # we want to schedule this to run one minute in the future
    # i'm not well versed enough in python to know the "right" way to format time
    # into a proper RFC3339 string.
    run_at = datetime.utcnow() + timedelta(minutes=5)
    run_at = run_at.isoformat()[:-7] + "Z"
    logging.info(f'run_at: {run_at}')
    
    client.queue("crawl-catalog", args=('pol',), queue="crawl-catalogs", reserve_for=60, at=run_at)