import psycopg2 as pg
from psycopg2.extras import DictCursor
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
        self.conn.autocommit = False
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
        self.conn = pg.connect(**self._connection_args())
        self.conn.autocommit = self.autocommit
        print("Connected to {}".format(self.host))
        self.cur = self.conn.cursor(cursor_factory=DictCursor)
        self.cur.execute("select version()")
        print(self.cur.fetchall())

    def _close(self):
        self.conn.commit()
        self.conn.close()

    def execute(self, sql : str ):
        """
        Execute an query that returns no results
        I.E. an insert, update, delete etc.
        :param sql:
        :return:
        """
        try:
            self.cur.execute(sql)
        except Exception as e:
            print("Unable to execute query")
            # in a context manager any failures here would automatically rollback() but doing it for good measure
            self.conn.rollback()
            raise e

    def query_to_list(self, sql):
        """
        Get results of a query in list form
        :param sql:
        :return: a list of dictionaries
        """
        try:
            self.cur.execute(sql)
            if self.cur.rowcount <= 0:
                return []

            return [dict(row) for row in self.cur]

        except Exception as e:
            print("Unable to execute query")
            # in a context manager any failures here would automatically rollback() but doing it for good measure
            self.conn.rollback()
            raise e

    def query_to_iter(self, sql, size=1000):
        """
        Get the results of a query in a generator
        :param sql:
        :param size:
        :return: a generator of dictionaries
        """
        self.cur.execute(sql)
        while True:
            try:
                results = self.cur.fetchmany(size)
                if not results: break
                for row in results:
                    yield dict(row)
            except Exception as e:
                print("Unable to execute query")
                raise e

