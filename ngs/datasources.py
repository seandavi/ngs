import sqlalchemy as sa

class UCSC(object):
    """
    This is a loose wrapper around `SQLalchemy <http://www.sqlalchemy.org/docs/>`_ for
    accessing the `UCSC Genome Browser <http://genome.ucsc.edu/>`_.

    Usage
    -----
    >>> import ngs.datasources
    >>> hg18 = ngs.datasources.UCSC()
    >>> tracks = hg18.getTrackDBDict()
    >>> print tracks.keys()[0:5]
    """
    
    
    def __init__(self,
                 uri="mysql://genome@genome-mysql.cse.ucsc.edu/",
                 db="hg18"):
        """
        :param uri: A SQLalchemy URI without the database name
        :param db: The database name
        """
        self.uri=uri + db
        self.engine=sa.create_engine(self.uri)
        self.db=db
        self.meta=sa.MetaData(self.engine)
        self.trackDB=sa.Table('trackDb',self.meta,autoload=True)

    def getTrackDBDict(self,typefilter=None):
        """
        Return a dict keyed by the track name of trackDB entries.
        :param typefilter: Filter the track type

        Example:
        >>> tracks = hg18.getTrackDBDict(typefilter='genePred')
        >>> tracks.has_key('refGene')
        """
        retdict = {}
        for i in self.trackDB.select(self.trackDB.c.type.contains(typefilter)).execute():
            retdict[i.tableName]=i
        return(retdict)

    def getTrack(self,trackname):
        """
        Given a trackname, get a SQLAlchemy track
        :param trackname: The name of the track
        :rettype: A SQLalchemy table object
        """
        try:
            return(sa.Table(trackname,self.meta,autoload=True))
        except:
            return(None)
