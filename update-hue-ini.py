## update-hue-ini.py
##
## This script will extract the appropriate IBM Analytics for Apache Hadoop credentials from the VCAP_SERVICES 
## environment variable inside a running container. It will add the username and password to the hue.ini file
## so that the hue application has access to a specific instance

import sys
import os
import json

username = None
password = None
webhdfsurl = None
srcfile = sys.argv[1]
destfile = sys.argv[2]

if "VCAP_SERVICES" in os.environ:
   vcaps = json.loads(os.environ["VCAP_SERVICES"])
   if "Analytics for Apache Hadoop" in vcaps:
     username = vcaps["Analytics for Apache Hadoop"][0]["credentials"]["userid"]
     password = vcaps["Analytics for Apache Hadoop"][0]["credentials"]["password"]

else:
   if "WEBHDFS_USER" in os.environ:
      username=os.environ["WEBHDFS_USER"]
   if "WEBHDFS_PASSWORD" in os.environ:
      password=os.environ["WEBHDFS_PASSWORD"]
   if "WEBHDFS_URL" in os.environ:
      webhdfsurl=os.environ["WEBHDFS_URL"]

if (username is not None and password is not None and webhdfsurl is not None):
   filedata = None
   with open (srcfile,'r') as file:
      filedata = file.read()

   filedata = filedata.replace('%instance_user%', username)
   filedata = filedata.replace('%instance_user_password%', password)
   filedata = filedata.replace('%webhdfs_url%', webhdfsurl)

   with open (destfile,'w') as file:
      file.write(filedata)
   sys.exit(0)
else:
   sys.stderr.write('Fatal error: cannot find Web HDFS credentials and/or endpoint\n')
   if username is None:
      sys.stderr.write('username missing\n')
   if password is None:
      sys.stderr.write('password missing\n')
   if webhdfsurl is None:
      sys.stderr.write('URL endpoint  missing\n')
   sys.exit(1)
