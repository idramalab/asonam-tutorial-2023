# Building a Continuous Social Media Data Collection System

As part of the [iDRAMA.cloud](https://idrama.cloud) project, we have put together this tutorial (originally [presented](https://asonam.cpsc.ucalgary.ca/2023/2023_asonam_program.pdf) at [ASONAM 2023](https://asonam.cpsc.ucalgary.ca/2023/) to help people build continuous data collection systems.

In addition to slides, this repository contains a functioning 4chan crawler with the following caveats:

* It is not optimized, especially with respect to database related operations.
* There is approximately zero error handling. You must be aware that at scale and over time, there will be a variety of errors, ranging from transient network issues to failures on the remote side to odd and unexpected issues with data.
* Documentation is very much lacking.
* I do not like Python and do not regularly use it.
* The design of this crawler is one of many possible and valid designs, and it has many limitations. That said, it works in approximately the same fashion as to our production crawler, but our production crawler makes use of other features of the [4chan API](https://github.com/4chan/4chan-API) to, e.g., handle boards that don't have an archive.

## Install

`pip install -r requirements.txt`

## Postgres

The most straight forward way to get Postgres running on a development environment is via Docker.

Pull the Postgres 14 image (newer versions should be fine as well):

`docker pull postgres:14`


Start up a Postgres container with a password of "testpassword":

`docker run -d --name postgres -p 5432:5432 -e POSTGRES_PASSWORD=testpassword postgres:14`

If you need direct access to psql, you can access via docker:
`docker exec -it postgres psql -U postgres`

## Faktory

See the [Faktory documentation](https://github.com/contribsys/faktory/wiki/Installation#docker)

## DB Migrations

I personally use [sqlx](https://github.com/launchbadge/sqlx), but that is because my production crawlers are written in Rust.

There are many other choices you go with, but this project uses sqlx.

The most straight forward way to get the sqlx cli program is to first get a local Rust environment by following the [installation instructions](https://www.rust-lang.org/learn/get-started).

Next, install the sqlx cli:

`cargo install sqlx-cli`

You should look at `sqlx --help` as well as the [README](https://github.com/launchbadge/sqlx/tree/main/sqlx-cli).

## Running things.

First, create a `.env` file so we don't store credentials in our repository.

`mkdir .env`

In that `.env` file put the following:

```
DATABASE_URL=postgres://postgres:testpassword@localhost:5432/chan_crawler
FAKTORY_URL=tcp://:testpassword@localhost:7419
```

Next, create your database and run migrations:

`sqlx database create`

Next, run migrations:

`sqlx migrate run`

Next, initialize a job to crawl /pol/ by running:

`python init_chan.py`

Finally, start up the the actual crawler by running:

`python chan_crawler.py`

