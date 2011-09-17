from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class EntrezGene(Base):
    __tablename__="entrezgene_main"

    id = Column(Integer, primary_key=True)
    tax_id  = Column(Integer)
    symbol  = Column(String(255))
    locustag = Column(String(255))
    chromosome = Column(String(255))
    map_location = Column(String(255))
    description  = Column(String(65535))
    type_of_gene = Column(String(255))
    nomenclature_symbol = Column(String(255))
    nomenclature_fullname = Column(String(65535))
    nomenclature_status = Column(String(255))
    modification_date = Column(String(255))

class GeneSynonyms(Base):
    __tablename__="entrezgene_synonyms"

    id = Column(Integer, primary_key=True)
    gene_id = Column(Integer, ForeignKey('entrezgene_main.id'))
    synonym = Column(String(65535))

