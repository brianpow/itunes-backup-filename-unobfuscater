#!/usr/bin/python

import sqlite3
import os
import argparse
import platform
from mbdb import Mbdb
import logging

def process_mbdb(path, filename, args):
    db = Mbdb(filename)
    mbdb = db.mbdb
    for index, row in list(mbdb.items()):
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
                log.debug("Renaming %s to %s" % (src, dst))
            try:
                if not args.dryrun:
                    os.renames(src, dst)
            except OSError:
                log.error("Error occured when renaming %s to %s" % (src, dst))
        elif row['filename'] != '':
            if args.verbose:
                log.info("Skipping root directory %s (%s)" % (row['domain'], row['fileID']))
        else:
            if args.verbose:
                log.info("Skipping directory %s (%s)" % (os.sep.join([row['domain'], row['filename']]), row['fileID']))

def validate_backup_path(path):
    files = ["Manifest.db", "Manifest.mbdb"]
    for file in files:
        if os.path.exists(os.sep.join([path, file])):
            return file
        
    return ""

def process_backup(path, file, args):
    db = os.sep.join([path, file])
    if file == 'Manifest.db':
        process_db(path, db, args)
    elif file == 'Manifest.mbdb':
        process_mbdb(path, db, args)

def process_db(path, filename, args):
    log.info("Processing %s..." % (filename))
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
                    log.info("%s\t%s" % (src, dst))
                else:
                    log.info("Renaming %s to %s" % (src, dst))
            
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
                        log.info("Error occured when finding source file: %s to %s" % (src, dst))
            except OSError:
                log.info("Error occured when renaming %s to %s" % (src, dst))

def main():
    parser = argparse.ArgumentParser(
        description='iTunes Backup Filename Unobfuscater. Licence: AGPL-v3.0')
    parser.add_argument('paths', default='', nargs='*',
                        help='Path of iTunes Backup [default: current working directory]')
    parser.add_argument('-d', '--dryrun', dest='dryrun',
                        action='store_true', help='Dry run, don\'t rename any files (default: %(default)s)')
    parser.add_argument('-u', '--undo', dest='undo',
                        action='store_true', help='Undo rename (default: %(default)s)')
    parser.add_argument('-v', '--verbose', dest='verbose',
                        action='count', help='Be more verbose')
    parser.add_argument('-t', '--tab', dest='tab',
                        action='store_true', help='print old and new name in tab separated format')
    parser.add_argument('-l','--log', 
    default='INFO', 
    choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    help='Set the logging level (default: %(default)s)'
    )
    args = parser.parse_args()
    parser.add_argument(
        '-V',
        '--version',
        action='version',
        version='%(prog)s 1.2')

    args = parser.parse_args()

    log_level = getattr(logging, args.log.upper(), logging.INFO)
    log.setLevel(log_level)
    
    
    if len(args.paths):
        for path in args.paths:
            file = validate_backup_path(path)
            if file:
                process_backup(path, file, args)
            else:
                log.warning("Unable to locate database file at %s" % (path))
                continue
    else:
        home = os.path.expanduser("~")
        
        backup_paths = ["."]
        if platform.system() == 'Darwin':
            backup_paths.append(os.sep.join(
                [home, 'Library/Application Support/MobileSync/Backup']))
        elif platform.system() == 'Windows':
            backup_paths.extend([
                os.sep.join([home, r'Apple\MobileSync\Backup']),
                os.sep.join([home, r'Apple Computer\MobileSync\Backup']),
                os.sep.join([home, r'AppData\Roaming\Apple\MobileSync\Backup']),
                os.sep.join([home, r'AppData\Roaming\Apple Computer\MobileSync\Backup'])
            ])

        valid_path = []
        
        for backup_path in backup_paths:
            if os.path.exists(backup_path):
                for folder in os.listdir(backup_path):
                    full_path=os.sep.join([backup_path, folder])
                    
                    if len(folder) == 40 and validate_backup_path(full_path):
                        valid_path.append(full_path)
                    else:
                         log.debug("%s is not a valid backup path" % (full_path))

        if len(valid_path) == 0:
            log.error("Unable to locate database file automatically.")
            return False
        
        if len(valid_path) > 1:
            for i, val in enumerate(valid_path):
                log.info("%2d: %s" % (i, val))
                index = input("Please select a path: ")
                path = valid_path[int(index)]
        elif len(valid_path) == 1:
            path = valid_path[0]
        
        file = validate_backup_path(path)
        process_backup(path, file, args)

logging.basicConfig(filename=f'{__name__}.log', level=logging.INFO, format = '%(asctime)s\t%(levelname)s\t%(message)s')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Add the handler to the root logger
logging.getLogger().addHandler(console)
log = logging.getLogger(__name__)

main()