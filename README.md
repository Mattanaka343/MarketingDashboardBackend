# Marketing Dashboard Backend

This repository contains the code for the backend of Nurvai and Wexpand's marketing dashboard. The backend presuposes a mysql database for the backend to connect to that contains the information. 

## Setup

In order to accurately run this dashboard we recoomend the following setup

```{bash}
conda create -n env mkt-dash-env python=3.12
conda activate mkt-dash-env

pip install -r requirements.txt
```

This ensures an environment is set that contains all the necessary packages. Alternatively you may use

```{bash}
python3 -m venv mkt-dash-env
source mkt-dash-env/bin/activate
pip install -r requirements.txt
```

if you prefer python vanilla environments

## The files

Files in this repository refer to the systems that make the dashboard run:

- `db` handles all queries to the database
- `routers` handles the routing of the data
- `services` manages the actual actions
- `dependencies.py` contains the parameters that are common to all api endpoints
- `utils.py` contains functions that are necessary in order to achieve the tasks of the services but that are unrelated to the actual services

We will now breakdown each section their main functions and setup they might all require

## DB

As was mentioned before db handles all the queries that relate to the database. This folder contains a single file that is called `queries.py` this file contains all the functions thtat relate to the queries.

### Setup 

For the queries to work propperly you first need to setup a .env file inside the folder.

```{bash}
touch .env
nano .env 
```

In this .env file you need to include the following:

- `HOST`: Where the mysql database is hosted
- `USER`: The user that will be used to access the database
- `PASSWORD`: The users password in order to access the database 
- `DB`: The name of the database in the sql schema

### Functions

The main functions of this file are the following:


