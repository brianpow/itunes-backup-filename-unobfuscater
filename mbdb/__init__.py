#!/usr/bin/env python
# https://stackoverflow.com/questions/3085153/how-to-parse-the-manifest-mbdb-file-in-an-ios-4-0-itunes-backup
import sys
import hashlib


class Mbdb:
    mbdx = {}
    mbdb = {}
    filename = ""

    def __init__(self, filename):
        self.filename = filename
        self.mbdb, self.mbdx = self.parse()
        for offset, fileinfo in list(self.mbdb.items()):
            if offset in self.mbdx:
                fileinfo['fileID'] = self.mbdx[offset]
            else:
                fileinfo['fileID'] = "<nofileID>"
                print("No fileID found for %s" % fileinfo_str(
                    fileinfo), file=sys.stderr)

    def getint(self, data, offset, intsize):
        """Retrieve an integer (big-endian) and new offset from the current offset"""
        value = 0
        while intsize > 0:
            value = (value << 8) + ord(data[offset])
            offset = offset + 1
            intsize = intsize - 1
        return value, offset

    def getstring(self, data, offset):
        """Retrieve a string and new offset from the current offset into the data"""
        if data[offset] == chr(0xFF) and data[offset + 1] == chr(0xFF):
            return '', offset + 2  # Blank string
        length, offset = self.getint(data, offset, 2)  # 2-byte length
        value = data[offset:offset + length]
        return value, (offset + length)

    def parse(self):
        data = open(self.filename, 'rb').read()
        if data[0:4] != "mbdb":
            raise Exception("This does not look like an MBDB file")
        mbdb = {}
        mbdx = {}
        offset = 4
        offset = offset + 2  # value x05 x00, not sure what this is
        while offset < len(data):
            try:
                fileinfo = {}
                fileinfo['start_offset'] = offset
                fileinfo['domain'], offset = self.getstring(data, offset)
                fileinfo['filename'], offset = self.getstring(data, offset)
                fileinfo['linktarget'], offset = self.getstring(data, offset)
                fileinfo['datahash'], offset = self.getstring(data, offset)
                fileinfo['unknown1'], offset = self.getstring(data, offset)
                fileinfo['mode'], offset = self.getint(data, offset, 2)
                fileinfo['unknown2'], offset = self.getint(data, offset, 4)
                fileinfo['unknown3'], offset = self.getint(data, offset, 4)
                fileinfo['userid'], offset = self.getint(data, offset, 4)
                fileinfo['groupid'], offset = self.getint(data, offset, 4)
                fileinfo['mtime'], offset = self.getint(data, offset, 4)
                fileinfo['atime'], offset = self.getint(data, offset, 4)
                fileinfo['ctime'], offset = self.getint(data, offset, 4)
                fileinfo['filelen'], offset = self.getint(data, offset, 8)
                fileinfo['flag'], offset = self.getint(data, offset, 1)
                fileinfo['numprops'], offset = self.getint(data, offset, 1)
                fileinfo['properties'] = {}
                for ii in range(fileinfo['numprops']):
                    propname, offset = self.getstring(data, offset)
                    propval, offset = self.getstring(data, offset)
                    fileinfo['properties'][propname] = propval
                mbdb[fileinfo['start_offset']] = fileinfo
                fullpath = fileinfo['domain'] + '-' + fileinfo['filename']
                id = hashlib.sha1(fullpath)
                mbdx[fileinfo['start_offset']] = id.hexdigest()
            except IndexError:
                print("Error when parsing %s" % (fileinfo['filename']))
                pass
        return mbdb, mbdx


def modestr(val):
    def mode(val):
        if (val & 0x4):
            r = 'r'
        else:
            r = '-'
        if (val & 0x2):
            w = 'w'
        else:
            w = '-'
        if (val & 0x1):
            x = 'x'
        else:
            x = '-'
        return r + w + x
    return mode(val >> 6) + mode((val >> 3)) + mode(val)


def fileinfo_str(f, verbose=False):
    if not verbose:
        return "(%s)%s::%s" % (f['fileID'], f['domain'], f['filename'])
    if (f['mode'] & 0xE000) == 0xA000:
        type = 'l'  # symlink
    elif (f['mode'] & 0xE000) == 0x8000:
        type = '-'  # file
    elif (f['mode'] & 0xE000) == 0x4000:
        type = 'd'  # dir
    else:
        print("Unknown file type %04x for %s" % (
            f['mode'], fileinfo_str(f, False)), file=sys.stderr)
        type = '?'  # unknown
    info = ("%s%s %08x %08x %7d %10d %10d %10d (%s)%s::%s" %
            (type, modestr(f['mode'] & 0x0FFF), f['userid'], f['groupid'], f['filelen'],
             f['mtime'], f['atime'], f['ctime'], f['fileID'], f['domain'], f['filename']))
    if type == 'l':
        info = info + ' -> ' + f['linktarget']  # symlink destination
    for name, value in list(f['properties'].items()):  # extra properties
        info = info + ' ' + name + '=' + repr(value)
    return info


verbose = True
if __name__ == '__main__':
    mbdb = Mbdb("Manifest.mbdb")
    print(mbdb.mbdb)
    mbdx = mbdb.mbdx
    for offset, fileinfo in list(mbdb.mbdb.items()):
        if offset in mbdx:
            fileinfo['fileID'] = mbdx[offset]
        else:
            fileinfo['fileID'] = "<nofileID>"
            print("No fileID found for %s" % fileinfo_str(
                fileinfo), file=sys.stderr)
        print(fileinfo_str(fileinfo, verbose))
