#
# HUE Filebrowser for IBM Analytics for Apache Hadoop service
#
#
# Pull base image.
FROM ubuntu:14.04.2

MAINTAINER David Carew <carew@us.ibm.com>

# Install required packages
RUN  \
 apt-get update && \
 apt-get install -y build-essential \
   python-dev \
   python-pip \
   rsync \  
   libsasl2-dev \ 
   libmysqlclient-dev \
   libkrb5-dev \
   libxml2-dev \
   libxslt-dev \
   libsqlite3-dev \
   libssl-dev \
   libldap2-dev \
   libgmp-dev
  

# Define working directory
WORKDIR /data

# Create an install directory
RUN mkdir install


# Copy Hue prod distribution with Bluemix changes
ADD hue-3.8.1-bluemix.tar.gz /data/install

# Uncomment this to write debug messages from Hue to stderr
#ENV DESKTOP_DEBUG true

# Need to add this to the import search path since we're sticking hueversion.py here 
ENV PYTHONPATH /data/install

# Remove hueversion.py symlinks and use a file containing the version info instead
RUN \
   find /data/install/hue-3.8.1-bluemix -name hueversion.py -exec rm {} \;
RUN \
   cp /data/install/hue-3.8.1-bluemix/VERSION  /data/install/hueversion.py

# Install Hue
RUN \
  cd /data/install/hue-3.8.1-bluemix && make install && rm -fr /data/install/hue-3.8.1-bluemix

# Add files to customize Hue config
ADD update-hue-ini.py /data/install/update-hue-ini.py
ADD hue-template.ini /data/install/hue-template.ini


# Script to start HUE
ADD start-hue.sh /data/install/start-hue.sh
RUN chmod +x /data/install/start-hue.sh 

# Hue listening on port 8000
EXPOSE 8000

CMD ["/data/install/start-hue.sh"]

