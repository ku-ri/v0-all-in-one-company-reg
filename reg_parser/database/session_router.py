from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.sql.dml import Delete, Update
from sqlalchemy.sql.elements import TextClause
import os

ENV = os.environ
echo = False

THEVCDB_ENGINES = {
    'primary' : create_engine(
        'postgresql+psycopg2://{USER}:{PW}@{HOST}:{PORT}/{DB_NAME}'.format(**{
            'USER' : os.environ['DB_USER'],
            'PW' : os.environ['DB_PW'],
            'HOST' : os.environ['MASTER_DB_HOST'],
            'PORT' : os.environ['DB_PORT'],
            'DB_NAME' : 'postgres'
    }), logging_name='primary', echo=echo),
    # 'replica' : create_engine(
    #     'postgresql+psycopg2://{USER}:{PW}@{HOST}:{PORT}/{DB_NAME}'.format(**{
    #         'USER' : os.environ['DB_USER'],
    #         'PW' : os.environ['DB_PW'],
    #         'HOST' : os.environ['REPLICA_DB_HOST'],
    #         'PORT' : os.environ['DB_PORT'],
    #         'DB_NAME' : 'thevcdb'
    # }), logging_name='replica', echo=echo)
}

APIDB_ENGINES = {
    'primary' : create_engine(
        'postgresql+psycopg2://{USER}:{PW}@{HOST}:{PORT}/{DB_NAME}'.format(**{
            'USER' : os.environ['DB_USER'],
            'PW' : os.environ['DB_PW'],
            'HOST' : os.environ['MASTER_DB_HOST'],
            'PORT' : os.environ['DB_PORT'],
            'DB_NAME' : 'thevcapi'
    }), logging_name='primary', echo=echo),
    # 'replica' : create_engine(
    #     'postgresql+psycopg2://{USER}:{PW}@{HOST}:{PORT}/{DB_NAME}'.format(**{
    #         'USER' : os.environ['DB_USER'],
    #         'PW' : os.environ['DB_PW'],
    #         'HOST' : os.environ['REPLICA_DB_HOST'],
    #         'PORT' : os.environ['DB_PORT'],
    #         'DB_NAME' : 'apidb'
    # }), logging_name='replica', echo=echo)
}

USERDB_ENGINES = {
    'primary' : create_engine(
        'postgresql+psycopg2://{USER}:{PW}@{HOST}:{PORT}/{DB_NAME}'.format(**{
            'USER' : os.environ['DB_USER'],
            'PW' : os.environ['DB_PW'],
            'HOST' : os.environ['MASTER_DB_HOST'],
            'PORT' : os.environ['DB_PORT'],
            'DB_NAME' : 'userdb'
    }), logging_name='primary', echo=echo),
    # 'replica' : create_engine(
    #     'postgresql+psycopg2://{USER}:{PW}@{HOST}:{PORT}/{DB_NAME}'.format(**{
    #         'USER' : os.environ['DB_USER'],
    #         'PW' : os.environ['DB_PW'],
    #         'HOST' : os.environ['REPLICA_DB_HOST'],
    #         'PORT' : os.environ['DB_PORT'],
    #         'DB_NAME' : 'userdb'
    # }), logging_name='replica', echo=echo)
}

class THEVCDBRoutingSession(Session):
    def get_bind(self, mapper=None, clause=None):
        if self._flushing or type(clause) in [Update, Delete] or\
            (type(clause) == TextClause and clause.text[:6] in ['INSERT', 'UPDATE', 'DELETE']):
            return THEVCDB_ENGINES['primary']
        else:
            # return THEVCDB_ENGINES['replica']
            return THEVCDB_ENGINES['primary']

class APIDBRoutingSession(Session):
    def get_bind(self, mapper=None, clause=None):
        if self._flushing or type(clause) in [Update, Delete] or\
            (type(clause) == TextClause and clause.text[:6] in ['INSERT', 'UPDATE', 'DELETE']):
            return APIDB_ENGINES['primary']
        else:
            # return APIDB_ENGINES['replica']
            return APIDB_ENGINES['primary']

class USERDBRoutingSession(Session):
    def get_bind(self, mapper=None, clause=None):
        if self._flushing or type(clause) in [Update, Delete] or\
            (type(clause) == TextClause and clause.text[:6] in ['INSERT', 'UPDATE', 'DELETE']):
            return USERDB_ENGINES['primary']
        else:
            # return USERDB_ENGINES['replica']
            return USERDB_ENGINES['primary']

# route
