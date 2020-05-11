# EVAN Services

Provides a postgis enabled postgres database for the EVAN project.


## Setup

* Install docker
* Install docker-compose (either pip or package manager)
* Move `db/env.bak` to `db/env` and enter credentials


## Run

From the `services` directory:

`docker-compose -p evan build`
`docker-compose -p evan up`
