import psycopg2 as pg
import os

class DB:
    def __init__(self, **kwargs):

        self.host = kwargs.get('host') if 'host' in kwargs else os.getenv("DB_HOST")
        self.port = kwargs.get('port') if 'port' in kwargs else os.getenv("DB_PORT")
        self.dbname = kwargs.get('dbname') if 'dbname' in kwargs else os.getenv("DB_NAME")
        self.user = kwargs.get('user') if 'user' in kwargs else os.getenv("DB_USER")
        self.password = kwargs.get('password') if 'user' in kwargs else os.getenv("DB_PASSWORD")
        self.autocommit = kwargs.get('autocommit', True)
        self._connect()

    def __enter__(self):
        self.connection.autocommit = False
        return self

    def __exit__(self, *exc):
        self._close()

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

    def _connect(self):
        self.connection = pg.connect(**self._connection_args())
        self.connection.autocommit = self.autocommit
        print("Connected to {}".format(self.host))
        self.cursor = self.connection.cursor()
        self.cursor.execute("select version()")
        print(self.cursor.fetchall())

    def _close(self):
        self.connection.commit()
        self.connection.close()

    def execute(self, sql):
        try:
            self.cursor.execute(sql)
            # return self.cursor.fetchall()
        except Exception as e:
            print("Unable to execute query")
            # in a context manager any failures here would automatically rollback() but doing it for good measure
            self.connection.rollback()
            raise e

