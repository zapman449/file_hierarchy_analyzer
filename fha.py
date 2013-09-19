#!/usr/bin/python

"""
Program to analyize the contents of a given directory (and subdirectories). 

Initial design: give counts of each extension type, and a break down by size
of the files into various buckets. Follows the pattern of:
    <1k, <10k, <100k, <500k, <1m, <500m, <1g, <500g, <1t, >1t
"""

import operator
import os
import os.path
import sys

sizebuckets = [
    (1024,          '<1kB'),
    (1024 * 10,     '<10kB'),
    (1024 * 100,    '<100kB'),
    (1024 * 500,    '<500kB'),
    (1024**2,       '<1mB'),
    (1024**2 * 500, '<500mB'),
    (1024**3,       '<1gB'),
    (1024**3 * 500, '<500gB'),
    (1024**4,       '<1tB'),
    (0,             '>1tB') ]

sizes = {}
for size,desc in sizebuckets :
    sizes[desc] = 0

extensions = {}

def get_extension(filename) :
    """returns the extension (text after last period), or None if no period is
    found (or is last char)."""
    index = filename.rfind('.')
    if index == -1 :
        return 'no_extension'
    elif index == len(filename) - 1 :
        # if last char
        return 'no_extension'
    else :
        extension = filename[index+1:]
        return extension

def size_parse(fullpath) :
    """takes a full path, and figure out how big it is, then add one to the
    right bucket"""
    if os.path.islink(fullpath) :
        return None
    try :
        stat = os.stat(fullpath)
    except :
        print 'error with file %s. skipping' % fullpath
        return None
    for size, desc in sizebuckets :
        if size == 0 :
            return desc
        elif stat.st_size < size :
            return desc

def usage() :
        print """USAGE:
%s <-h|--help>
    print this message
%s <directory>
    analyze <directory>
%s
    analyze current directory (equal to '%s .')""" % (sys.argv[0], sys.argv[0], sys.argv[0], sys.argv[0])

def gather(workingdir) :
    """walk the directory, gathering size and extension data"""
    if not os.path.isdir(workingdir) :
        print "ERROR: directory %s is not a valid directory" % workingdir
    filecount = 0
    for root, dirs, files in os.walk(workingdir) :
        for filename in files :
            filecount += 1
            fullpath = os.path.join(root, filename)
            size = size_parse(fullpath)
            if size == None :
                continue
            sizes[size] += 1
            extension = get_extension(filename)
            try :
                extensions[extension] += 1
            except :
                extensions[extension] = 1
    print "total file count is %d" % filecount
    print

def report_sizes() :
    """using the sizes dictionary, report on sizes"""
    print "size                count"
    for size,desc in sizebuckets :
        print "%6s        %10d" % (desc, sizes[desc])
    print

def report_extensions() :
    """using the extensions dictionary, report on extensions"""
    sorted_ext = sorted(extensions.iteritems(), key=operator.itemgetter(1),
                        reverse=True)
    print "   extension         count (top ten list)"
    for extension, count in sorted_ext[:10] :
        print "%12s  %10d" % (extension, count)

if __name__ == '__main__' :
    if len(sys.argv) == 1 :
        workingdir = '.'
    elif sys.argv[1] in ('-h' or '--help') :
        usage()
        sys.exit(0)
    else :
        workingdir = sys.argv[1]
    gather(workingdir)
    report_sizes()
    report_extensions()
