#!/usr/bin/python

import sqlite3
import os
import argparse
from mbdb import Mbdb


def process_mbdb(filename):
    db = Mbdb(filename)
    mbdb = db.mbdb
    for index, row in mbdb.items():
        if (row['mode'] & 0xE000) != 0x4000:
            if args.undo:
                dst = os.sep.join([path, row['fileID']])
                src = os.sep.join(
                    [path, row['domain'], row['filename'].replace('/', os.sep)])
            else:
                src = os.sep.join([path, row['fileID']])
                dst = os.sep.join(
                    [path, row['domain'], row['filename'].replace('/', os.sep)])
            if args.verbose:
                print "Renaming %s to %s" % (src, dst)
            try:
                if not args.dryrun:
                    os.renames(src, dst)
            except OSError:
                print "Error occured when renaming %s to %s" % (src, dst)
        elif row['filename'] != '':
            if args.verbose:
                print "Skipping root directory %s (%s)" % (row['domain'], row['fileID'])
        else:
            if args.verbose:
                print "Skipping directory %s (%s)" % (os.sep.join([row['domain'], row['filename']]), row['fileID'])


def process_db(filename):
    print "Processing %s..." % (filename)
    conn = sqlite3.connect(filename)

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
                if args.tab:
                    print "%s\t%s" % (src, dst)
                else:
                    print "Renaming %s to %s" % (src, dst)
            
            try:
                if not args.dryrun:
                    try:
                        os.stat(src)
                        try:
                            if (os.stat(dst)):
                                os.remove(dst)
                        except OSError:
                            pass
                        os.renames(src, dst)
                    except OSError:
                        print "Error occured when finding source file: %s to %s" % (src, dst)
            except OSError:
                print "Error occured when renaming %s to %s" % (src, dst)


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
parser.add_argument('-t', '--tab', dest='tab',
                    action='store_true', help='print old and new name in tab separated format')
parser.add_argument(
    '-V',
    '--version',
    action='version',
    version='%(prog)s 1.2')

args = parser.parse_args()

for path in args.paths:
    db = os.sep.join([path, 'Manifest.db'])
    db2 = os.sep.join([path, 'Manifest.mbdb'])
    if os.path.isfile(db):
        process_db(db)
    elif os.path.isfile(db2):
        process_mbdb(db2)
    else:
        print "Unable to locate database file at %s or %s" % (db, db2)
        continue
