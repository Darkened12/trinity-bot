from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Database:
    base = None

    def __init__(self, db_name='sqlite:///:memory:', new_database=False):
        self.db_name = db_name
        self.new_database = new_database
        self.engine = self._get_engine()
        self.session = self._get_session()

    def _get_engine(self):
        engine = create_engine(self.db_name)
        if self.new_database:
            self.base.metadata.create_all(engine)
        return engine

    def _get_session(self):
        Session = sessionmaker(bind=self.engine)
        return Session()

