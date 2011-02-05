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

    def getSampleSheetByStudyID(self,study_id):
        """
        Get the sample sheet from the database for a given Study ID.

        :param study_id: Study id to match
        :type study_id: Int
        :rtype: dict('keys':column names from database,'rows':The actual rows for the records)
        """
        con = self.engine.connect()
        res = con.execute("""
select distinct 
	   r1.Flowcell, 
       r1.Lane, 
       r1.sequenceFile as r1sequence, 
       r2.sequenceFile as r2sequence,
       solexa_source.name as source_name,
       solexa_sample.name as sample_name,
       solexa_library.name as library_name,
       solexa_study.id as study_id,
       solexa_study.study_title as study_title,
       solexa_sample.variable as sample_variable,
       solexa_sample.sample_type,
       solexa_run.id as run_id,
       solexa_lane.id as lane_id,
       solexa_source.id as source_id,
       solexa_sample.id as sample_id,
       solexa_library.id as library_id,
       r1.`Paired-End`,
       r1.index_read,
       r1.pooled_library
from (select * from solexa_alignment where Read_Direction=0) r1 
	left outer join
    (select sequenceFile, Flowcell, Lane from solexa_alignment where Read_Direction=1) r2 
    on r1.flowcell=r2.flowcell and r1.lane=r2.lane
    join solexa_run on r1.flowcell=solexa_run.FlowCell
    join solexa_lane on solexa_run.id=solexa_lane.run_id and r1.lane=solexa_lane.lane
    join solexa_library on solexa_lane.library_id=solexa_library.id
    join `solexa_sample_library` on solexa_sample_library.library_id=solexa_library.id 
    join solexa_sample on solexa_sample_library.sample_id=solexa_sample.id
    join solexa_source_sample on solexa_source_sample.sample_id=solexa_sample.id
    join solexa_source on solexa_source.id=solexa_source_sample.source_id
    join solexa_study_sample on solexa_study_sample.sample_id=solexa_sample.id
    join solexa_study on solexa_study.id=solexa_study_sample.study_id
    where study_id=%d
""" % (study_id))
        keys = res.keys()
        return({'keys':res.keys(),'rows':res.fetchall()})


    

