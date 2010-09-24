import sqlalchemy.orm
import sqlalchemy as sa

class SolexaDB:
    """
    Little helper class for working with the solexa database.

    The class is built using `sqlalchemy <http://www.sqlalchemy.org/>`_ so reading the `docs <http://www.sqlalchemy.org/docs/>`_ is likely to be helpful.

    >>> import ngs.solexadb.model
    >>> sdb = ngs.solexadb.model.SolexaDB("mysql://sdavis:mic2222@localhost/solexa")
    >>> sm = sdb.getTable('solexa_matrix')
    >>> session = sdb.getSession()
    >>> session.query(sm.c.Source_Name).filter(sm.c.Study_ID==7).slice(1,10).count()
    9L

    """
    
    def __init__(self,uri):
        self.engine = sa.create_engine(uri)
        self.meta = sa.MetaData()
        self.meta.bind = self.engine
        self.meta.reflect()
        self.Session = sqlalchemy.orm.sessionmaker(bind=self.engine)

    def getTables(self):
        """
        Get tables available in the database.

        :rtype: A dict of :class:`sqlalchemy.Table` objects keyed by name
        """
        return(self.meta.tables)

    def getTable(self,name):
        """
        Return a sqlAlchemy Table object associated with the table name

        :param name: The table name to grab
        :type name: string
        :rtype: A :class:`sqlalchemy.Table` object
        """
        try:
            return self.meta.tables[name]
        except:
            # could still be a view, so we need to expressly create
            # the table object
            try:
                return(sa.Table(name,self.meta,autoload=True))
            except:
                "Unable to return table"

    def getSession(self):
        """
        Get an active Session object.

        :rtype: An object of type :class:`sqlalchemy.orm.Session`
        """
        return(self.Session())
    

