"""Running pylint with the updated pythonpath."""

import os
import sys
import subprocess

def usage():
    """."""
    
    sys.stderr.write("%s <input files>\n" % sys.argv[0])
    sys.stderr.write("\tif you provide multiple files they are run together.\n")

def main():
    """."""

    if len(sys.argv) < 2:
        print "params count: %d" % len(sys.argv)
        print "params: %s" % sys.argv[1:]
        usage()
        sys.exit(-1)

    args = ['pylint', '--rcfile=py.config']
    args.extend(sys.argv[1:])

    process = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE)

    output = process.communicate()[0]
    
    print output

    # --------------------------------------------------------------------------
    # Done.    

if __name__ == "__main__":
    main()
