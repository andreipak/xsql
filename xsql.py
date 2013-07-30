#!/usr/bin/env python

from ConfigParser import SafeConfigParser, NoOptionError
from optparse import OptionParser
import sys, os

usage = "usage: %prog [options] query"
parser = OptionParser(usage=usage)
parser.add_option("-c", "--configfile",
                  metavar="CONFIG",
                  default="xsql.cfg",
                  help="configuration file path"
                  " [default: %default]")

parser.add_option("-s", "--section",
                  help="section name in configuration file, "
                  "default: first section")

(opt, args) = parser.parse_args()

configfile = opt.configfile

config = SafeConfigParser()
config.read([configfile, os.path.expanduser('~/.xsql.cfg')])

section = opt.section or "default"
module = config.get(section, 'module')

db_mod = __import__(module)
if hasattr(db_mod, 'connect'):
    connect = db_mod.connect
else:
    raise ImportError('Can not use %s.connect() function')
    sys.exit(2)

connect_args = config.get(section, 'connect')
connect_args = eval(connect_args)

if isinstance(connect_args, basestring):
    con = connect(connect_args)
elif isinstance(connect_args, tuple):
    con = connect(*connect_args)
elif isinstance(connect_args, dict):
    con = connect(**connect_args)
else:
    print "Can not load arguments for connect(): \
    unknown type - %r" % type(connect_args)
    sys.exit(1)

delimiter = config.get(section, 'delimiter')
delimiter = eval(delimiter)

if len(args) == 1:
    query = args[0]
elif len(args) > 1:
    print "More than one query specified: %r" % args
    sys.exit(1)
else:
    try:
        query = config.get(section, 'query')
        query = eval('%s' % query)
    except NoOptionError:
        print "There is no query to execute"
        sys.exit(1)

c = con.cursor()
result = c.execute(query)

if result or c.rowcount > 0:
   print delimiter.join(map(str, map(lambda x: x[0], c.description)))
    for row in c.fetchall():
        print delimiter.join(map(str, row))
else:
    print "empty set."

try:
    if config.get(section, 'commit').lower() in ("1", "true"):
        con.commit()
except NoOptionError:
    pass

c.close()
con.close()
