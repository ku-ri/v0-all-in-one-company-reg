import os
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from .session_router import (
    THEVCDBRoutingSession, THEVCDB_ENGINES,
    APIDBRoutingSession, APIDB_ENGINES,
    USERDBRoutingSession, USERDB_ENGINES
)

ENV = os.environ

class Connection(object):
    def __init__(self, engines):
        echo = True if int(ENV['FLASK_DEBUG']) else False
        self.engines = engines
        # self.engine = create_engine('postgresql+psycopg2://{0}:{1}@{2}/{3}'.format(
        #     ENV['DB_USER'], ENV['DB_PW'], ENV['DB_HOST'], db_name), echo=echo)

    # def connect(self):
    #     self.conn = self.engine.connect()
    #
    # def connectExist(self):
    #     self.Base = automap_base()
    #     self.Base.prepare(self.engine, reflect=True)

    def dispose(self):
        for k, engine in self.engines.items():
            engine.dispose()
        return

    def startSession(self, sessionRouter):
        Session = scoped_session(sessionmaker(class_=sessionRouter))
        self.session = Session()
        return



class THEVCDB(Connection):
    def __init__(self):
        super(THEVCDB, self).__init__({
            # 'read' : THEVCDB_ENGINES['replica'],
            'read' : THEVCDB_ENGINES['primary'],
            'write' : THEVCDB_ENGINES['primary']
        })
        self.Base = automap_base()
        self.Base.prepare(self.engines['read'], reflect=True)

    def startSession(self):
        super(THEVCDB, self).startSession(THEVCDBRoutingSession)



class APIDB(Connection):
    def __init__(self):
        super(APIDB, self).__init__({
            # 'read' : APIDB_ENGINES['replica'],
            'read' : APIDB_ENGINES['primary'],
            'write' : APIDB_ENGINES['primary']
        })
        self.Base = automap_base()
        self.Base.prepare(self.engines['read'], reflect=True)

    def startSession(self):
        super(APIDB, self).startSession(APIDBRoutingSession)


class USERDB(Connection):
    def __init__(self):
        super(USERDB, self).__init__({
            # 'read' : USERDB_ENGINES['replica'],
            'read' : USERDB_ENGINES['primary'],
            'write' : USERDB_ENGINES['primary']
        })
        self.Base = automap_base()
        self.Base.prepare(self.engines['read'], reflect=True)

    def startSession(self):
        super(USERDB, self).startSession(USERDBRoutingSession)


# Let`s do it
