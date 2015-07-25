## Overview

This is a port of the [HUE - Hadoop User Experience](http://gethue.com) file browser application that works with
the [IBM Analytics for Apache Hadoop Service](https://www.ng.bluemix.net/docs/services/AnalyticsforHadoop/index.html) in IBM Bluemix. It is a Docker image that should be
run in the IBM Containers Docker Environment 

## Background

HUE - the Hadoop User Experience is an open source set of applications for managing Hadoop Clusters that works with most Hadoop distros 
including the standalone version of the  [IBM Open Platform with Apache Hadoop](http://www-03.ibm.com/software/products/en/ibm-open-platform-with-apache-hadoop).

The IBM Analytics for Apache Hadoop Service in Bluemix is powered by the IBM Open Platform with Apache Hadoop  but deviates from
the standalone version of the IBM Open Platform because it uses Basic Authentication to protect the  WebHDFS URL. Because of this wrinkle, out of the box, the HUE file browser does
not work with the IBM Analytics for Apache Hadoop Service. This project can be used to create a Docker image based on HUE 3.8.1 (with a few code modifications required
to support the way  WebHDFS is implemented by the IBM Analytics for Apache Hadoop Service in Bluemix) to provide a GUI file browser to make HDFS file management easier.

When run in the [IBM Containers] (https://www.ng.bluemix.net/docs/containers/container_index.html) environment bound to an app that is bound to an instance of the
IBM Analytics for Apache Hadoop Service, this image will automatically discover the credentials and URLs needed to access HDFS in the service instance. If run in
another Docker environment the credentials and URLs to access the IBM Analytics for Apache Hadoop Service's WebHDFS endpoint must be provided via environment variables.

> *DISCLAIMER* 
> Note that in this image all the other HUE apps are present but have been blacklisted in the hue.ini 
> file so only the file browser can be used - it is the only one that  has been tested. 
> The instructions to run HUE on standalone alone version of IBM Open Platform with Apache Hadoop are [here](https://developer.ibm.com/hadoop/blog/2015/06/02/deploying-hue-on-ibm-biginsights/)
> Consult  these instructions if you would like to get more HUE apps running against the IBM Analytics for Apache Hadoop Service.
> Note that additional tweaking (a la the file browser) may be required to get the other apps running as well. 


## What you need to get started

- A Bluemix account 
    [Sign up](https://console.ng.bluemix.net/?cm_mmc=IBMEcoDWW-_-IIC-_-BluemixDay-_-BluemixDayAAAWebpage) in Bluemix, or use an existing account.
- A Docker client + CloudFoundry CLI setup on Windows, Mac or Linux 
   Follow the instructions for setting up the IBM Containers Plugin for  Cloud Foundry [here] (https://www.ng.bluemix.net/docs/containers/container_cli_cfic.html#container_cli_cfic)
   *Note: The Docker binary that you are told to download must be Docker 1.6.x. On Windows it must be renamed to **docker.exe** and be in the PATH. On Mac it must be renamed to **docker**, made executable and be in the PATH.*
- Login into Bluemix and to IBM Containers  with the following sequence of commands:
```sh
  cf login
  cf ic login
```
- In the Bluemix dashboard at (http://bluemix.net) click on **START CONTAINERS**. If you've never used IBM Containers before you'll be prompted to provide a unique suffix for 
your private image repository.
- Back on the command line,  copy the image to your private repository by issuing the following command   (note replace foobar with the unique suffix to your private repository)
```sh
   cf ic cpi djccarew/hue-filebrowser-bluemix  registry.ng.bluemix.net/foobar/hue-filebrowser-bluemix
```

## Getting the HUE file browser image  up and running

### 1. Create a Bluemix app with the IBM Analytics for Apache Hadoop Service

  1. In the Bluemix dashboard click on **CREATE APP**
  2. Click on **Web**
  3. Click on **SDK for Node.js**
  4. Click on **CONTINUE**
  5. Give the app a system wide unique name and click **FINISH**
  6. When the message indicates that your app has started, click on the **Back to Dashboard** link 
  7. Under **Applications** click on your application's rectangle
  8. Click on **ADD A SERVICE OR API**, and then scroll down to the **Data & Analytics** section
  9. Click on **Analytics for Apache Hadoop** and then click **CREATE**
  10. When the message indicates that your app has restarted, click on the **Back to Dashboard** link 

### 2. Create a running instance of the Docker image
  1. In the Bluemix dashboard click on **START CONTAINERS**
  2. Click on the icon for the *hue-filebrowser-bluemix* image
  3. Give the container a name and select **Request and Bind Public IP** under **Public IP Address**
  4. Enter *8000* under **Public Ports**
  5. Expand **Advanced Options** and select the app you created in the previous section under **Service Binding**
  6. Click **CREATE** and wait until the container shows as being started
  7. Note the Public IP assigned to the container once it has been started

### 3. Running the HUE File Browser
  1. Enter the URL *[Container IP]:8000/filebrowser* where *[Container IP]* is the IP bound  to the  container. For example if the IP is *136.168.88.76* the URL would be *http://136.168.88.76:8000/filebrowser* 
  2. Enter `hue` as the username (note no password is required and any username will do )
  3. Verify that you're able to navigate through the HDFS file system on your instance of IBM Analytics for Apache Hadoop Service. You'll have the permissions of the username specified in the service's meta data 

## Modifications made to original HUE 3.8.1 source code
[../hue-3.8.1-bluemix/desktop/core/src/desktop/conf.py](https://raw.githubusercontent.com/ibmecod/bluemix-hue-filebrowser/master/hue-3.8.1-bluemix/desktop/core/src/desktop/conf.py)
Added another config object available via hue.ini that contains the password needed for Basic Authentication against the WebHDFS endpoint

[../hue-3.8.1-bluemix/desktop/core/src/desktop/auth/views.py](https://raw.githubusercontent.com/ibmecod/bluemix-hue-filebrowser/master/hue-3.8.1-bluemix/desktop/core/src/desktop/auth/views.py)
Commented out code that assumes the hue user is the hdfs user and tries to create a hdfs home directory 

[../hue-3.8.1-bluemix/desktop/libs/hadoop/src/hadoop/fs/webhdfs.py](https://raw.githubusercontent.com/ibmecod/bluemix-hue-filebrowser/master/hue-3.8.1-bluemix/desktop/libs/hadoop/src/hadoop/fs/webhdfs.py)
Modified code that accesses the WebHDFS URL to use Basic Authentication

