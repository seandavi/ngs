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
        select fcia.flowcellName,sr.date,r1.lane,nread,read1,read2,index_read,sequenceFile1,sequenceFile2,sequenceFile3,ssource.name as source_name,ssource.id as source_id,samp.name as sample_name,samp.id as sample_id,samp.variable as sample_variables,slib.name as library_name,slib.id as library_id, solexa_study.id as study_id, solexa_study.study_title from soldb.flowCellBasecallLane fcbcl
join (select basecallFile as sequenceFile1,lane,basecallId from soldb.flowCellBasecallLane where readnumber=0) as r1 on r1.basecallId=fcbcl.basecallId and fcbcl.lane=r1.lane and fcbcl.readnumber=0
left outer join (select basecallFile as sequenceFile2,lane,basecallId from soldb.flowCellBasecallLane where readnumber=1) as r2 on r2.basecallId=fcbcl.basecallId and r2.lane=r1.lane
left outer join (select basecallFile as sequenceFile3,lane,basecallId from soldb.flowCellBasecallLane where readnumber=2) as r3 on r3.basecallId=fcbcl.basecallId and r3.lane=r2.lane
join flowCellBasecall fcbc on fcbcl.basecallId=fcbc.id
join solexa.uniqueByMaxDateFlowCellBaseCallLane u on fcbc.id=u.basecallid and fcbcl.lane=u.lane
join flowCellImageAnalysis fcia on fcbc.imageAnalysisId=fcia.id
join solexa_run sr on sr.flowcell=fcia.flowcellName
join solexa_lane sl on sr.id=sl.run_id and sl.lane=fcbcl.lane
join solexa_library slib on slib.id=sl.library_id
join solexa_sample_library samplib on samplib.library_id=slib.id
join solexa_sample samp on samp.id=samplib.sample_id
join solexa_source_sample soursamp on soursamp.sample_id=samp.id
join solexa_source ssource on ssource.id=soursamp.source_id
join solexa_study_sample on solexa_study_sample.sample_id=samp.id
join solexa_study on solexa_study_sample.study_id=solexa_study.id
where study_id=%d
""" % (study_id))
        keys = res.keys()
        return({'keys':res.keys(),'rows':res.fetchall()})


    

