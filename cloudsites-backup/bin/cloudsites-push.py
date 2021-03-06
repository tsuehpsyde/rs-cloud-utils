#!/usr/bin/python -tt
# cloudsites-rotate.py - A simple script to login to our Rackspace Cloud Files
# and rotate our backups for Rackspace Cloud Sites.

import os
import sys

# We need to make sure we have these locally.
import cloudfiles

# Get our personal info
from config import *

# This is a work-around for this issue:
# https://github.com/rackspace/python-cloudfiles/issues/34
#
# How many times you wish to re-try until giving up.

# Cron servers do not have SSL =(
#from ssl import SSLError
loopNumber, maxLoopNumber, uploaded = 0, 5, False

def usage():
    prog = os.path.basename(sys.argv[0])
    msg = "%s - Script to upload CloudSites backups.\n" % (prog,)
    msg += "Usage: %s [FILE]\n" % (prog,)
    sys.stdout.write(msg)
    sys.exit(1)

# Make sure we are given ONE file to upload
if len(sys.argv) != 2:
    usage()

# The file to upload.
localFile = sys.argv[1]

# Make sure the file exists
if not os.path.isfile(localFile):
    usage()

# Remove the path when naming it on Cloud Files
filename = os.path.basename(localFile)

# Connect to Rackspace Cloud Files with our API
conn = cloudfiles.get_connection(username, apiKey)

# Get our container object for where we plan to back everything up to.
# This could be just the creation call, but that seems hacky.
try:
    ourContainer = conn.get_container(backupContainer)
except:
    ourContainer = conn.create_container(backupContainer)

# Upload our file.
while loopNumber < maxLoopNumber and not uploaded:
    try:
        loopNumber += 1
        msg = "INFO: (Attempt #%d) Uploading %s to %s..." % (loopNumber, filename, backupContainer)
        sys.stdout.write(msg)
        sys.stdout.flush()
        ourBackup = ourContainer.create_object(filename)
        ourBackup.load_from_filename(localFile)
        sys.stdout.write('done.\n')
        sys.stdout.flush()
        uploaded = True
    # Cron servers do not have SSL =(
    #except SSLError:
    except:
        msg = "failed.\n"
        msg += "ERROR: Upload of %s failed.\n" % (filename,)
        sys.stdout.write(msg)
        sys.stdout.flush()

# All done.
sys.exit(0)
