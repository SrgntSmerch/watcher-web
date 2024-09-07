from peewee import MySQLDatabase
from flask import g
from cfg import config

# import logging

# Enable logging
# logger = logging.getLogger('peewee')
# logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)

db = MySQLDatabase(database=config.database_name,
                   user=config.database_user,
                   password=config.database_password,
                   host=config.database_host)

def get_db():
    """Get or open a connection to the database."""
    if 'db' not in g:
        g.db = db
        g.db.connect()
    return g.db

def close_db(e=None):
    """Close the database connection if it exists."""
    db = g.pop('db', None)
    if db is not None:
        db.close()