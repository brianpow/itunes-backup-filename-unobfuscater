#!/usr/bin/python

import sqlite3
import os
import argparse

parser = argparse.ArgumentParser(
    description='iTunes Backup Filename Unobfuscater. Licence: AGPL-v3.0')
parser.add_argument('paths', default='.', nargs='*',
                    help='Path of iTunes Backup [default: current working directory]')
parser.add_argument('-d', '--dryrun', dest='dryrun',
                    action='store_true', help='Dry run, don\'t rename any files')
parser.add_argument('-u', '--undo', dest='undo',
                    action='store_true', help='Undo rename')
parser.add_argument('-v', '--verbose', dest='verbose',
                    action='count', help='Be more verbose')
parser.add_argument(
    '-V',
    '--version',
    action='version',
    version='%(prog)s 1.0')

args = parser.parse_args()

for path in args.paths:
    db = os.sep.join([path, 'Manifest.db'])
    if not os.path.isfile(db):
        print "Unable to locate database file at %s" % (db)
        continue
    print "Processing %s..." % (db)
    conn = sqlite3.connect(db)

    c = conn.cursor()
    for row in c.execute('SELECT * FROM Files'):
        if row[3] == 1:
            if args.undo:
                dst = os.sep.join([path, row[0][:2], row[0]])
                src = os.sep.join([path, row[1], row[2]])
            else:
                src = os.sep.join([path, row[0][:2], row[0]])
                dst = os.sep.join([path, row[1], row[2]])
            if args.verbose:
                print "Renaming %s to %s" % (src, dst)
            try:
                if not args.dryrun:
                    os.renames(src, dst)
            except OSError:
                print "Error occured when renaming %s to %s" % (src, dst)
