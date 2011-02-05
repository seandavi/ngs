from ngs.main import subparsers
import ngs.solexadb.model

def func(args):
    sdb = ngs.solexadb.model.SolexaDB(args.uri)
    res = sdb.getSampleSheetByStudyID(args.study_id)
    print "\t".join([str(x) for x in res['keys']])
    for row in res['rows']:
        print "\t".join([str(x) for x in row])

subparser = subparsers.add_parser(
    'makeSampleSheet',
    help="Generate a standard sample sheet for a given study id")
subparser.add_argument(
    "-u","--uri",dest='uri',
    help="Database uri, like 'mysql://username:password@localhost/solexa'")
subparser.add_argument(
    "-s","--study-id",dest='study_id',type=int,
    help="Study ID from the solexa database")
subparser.set_defaults(func=func)
