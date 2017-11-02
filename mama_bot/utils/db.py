import psycopg2 as pg
import os
from contextlib import contextmanager

class DB:

    def __init__(self, **kwargs):

        self.host = kwargs.get('host') if 'host' in kwargs else os.getenv("DB_HOST")
        self.port = kwargs.get('port') if 'port' in kwargs else os.getenv("DB_PORT")
        self.dbname = kwargs.get('dbname') if 'dbname' in kwargs else os.getenv("DB_NAME")
        self.user = kwargs.get('user') if 'user' in kwargs else os.getenv("DB_USER")
        self.password = kwargs.get('password') if 'user' in kwargs else os.getenv("DB_PASSWORD")

    def __enter__(self):
        ...

    def __exit__(self):
        ...


    def _connection_args(self) -> dict:
        return  {'host':self.host,
                 'port':self.port,
                 'dbname':self.dbname,
                 'user':self.user,
                 'password': self.password}


    def _connection_str(self):
        return "host {} port {} dbname {} user {} password".format(self.host,
                                                                   self.port,
                                                                   self.dbname,
                                                                   self.user,
                                                                   self.password)

    @contextmanager
    def connect(self):
        try:
            with pg.connect(**self._connection_args()) as conn:
                with conn.cursor() as cursor:
                    yield cursor
            conn.close()
        except Exception as e:
            print('Unable to run query')
            raise e

# db = DB()
# with db.connect() as cur:
#     cur.execute("select version()")
#     print(cur.fetchall())