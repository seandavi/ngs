#!/usr/bin/env python
import ngs.solexadb.model
import optparse

def main():
    parser = optparse.OptionParser()
    parser.add_option("-u","--uri",dest='uri',
                      help="Database uri, like 'mysql://sdavis:mic2222@localhost/solexa'")
    parser.add_option("-s","--study-id",dest='study_id',type='int',
                      help="Study ID from the database")
    (opts,args)=parser.parse_args()
    if((opts.uri is None) | (opts.study_id is None)):
        exit(1)
    sdb = ngs.solexadb.model.SolexaDB(opts.uri)
    res = sdb.getSampleSheetByStudyID(opts.study_id)
    print "\t".join([str(x) for x in res['keys']])
    for row in res['rows']:
        print "\t".join([str(x) for x in row])

main()
