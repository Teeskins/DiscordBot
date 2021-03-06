# Teeskins Discord bot

## How to build and run ?

1. Install the dependencies 
- Python3
- MariaDB

```bash
python3 -m pip install -r requirements.txt
```

1. Create the file `config.ini` in the repository source using the `config_example.ini`
    - Insert a discord token
    - Complete the database fields

2. Import the SQL schema into a db engine, for MariaDB:
   - `mariadb -u username -p database_name < sql/scheme.sql`

3. Execute the file `main.py` with python3 (version <= `3.8`) to start the bot

## Docker

To download the submodules
```bash
git submodule init
git submodule update
```

Launch containers

```bash
TW_UTILS_PORT=3000 docker-compose up
```
