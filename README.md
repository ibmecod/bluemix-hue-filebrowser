## Overview

This is a port of the [HUE - Hadoop User Experience](http://gethue.com) file browser application that works with
the [IBM Analytics for Apache Hadoop Service](https://www.ng.bluemix.net/docs/services/AnalyticsforHadoop/index.html) in IBM Bluemix. It is a Docker image that should be
run in the IBM Containers Docker Environment 

## Background

HUE - the Hadoop User Experience is an open source set of applications for managing Hadoop Clusters that works with most Hadoop distros 
including the standalone version of the  [IBM Open Platform with Apache Hadoop](http://www-03.ibm.com/software/products/en/ibm-open-platform-with-apache-hadoop).

The IBM Analytics for Apache Hadoop Service in Bluemix is powered by the IBM Open Platform with Apache Hadoop  but deviates from
the standalone version of the IBM Open Platform in the way WebHDFS URL is protected. Because of this wrinkle, the HUE file browser does
not work with the IBM Analytics for Apache Hadoop Service out of the box. This project can be used to create a Docker image based on HUE 3.8.1
that has the code modifications required to support the way WebHDFS authentication is implemented by the IBM Analytics for Apache Hadoop Service in Bluemix. 

When run in the [IBM Containers] (https://www.ng.bluemix.net/docs/containers/container_index.html) environment and  bound to an app that is bound to an instance of the
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
- A Docker 1.6.x  client 
  - On 32bit Windows download the client from [here](https://get.docker.com/builds/Windows/i386/docker-1.6.2.exe), rename it to **docker.exe** and put it somewhere in your PATH
  - On 64bit Windows download the client from [here](https://get.docker.com/builds/Windows/x86_64/docker-1.6.2.exe), rename it to **docker.exe** and put it somewhere in your PATH  
  - On 32bit Linux download the client from [here](https://get.docker.com/builds/Linux/i386/docker-1.6.2), rename it to **docker**, make it executable  and put it somewhere in your PATH
  - On 64bit Linux download the client from [here](https://get.docker.com/builds/Linux/x86_64/docker-1.6.2), rename it to **docker**, make it executable  and put it somewhere in your PATH
  - On 32bit Mac OS X download the client from [here](https://get.docker.com/builds/Darwin/i386/docker-1.6.2), rename it to **docker**, make it executable  and put it somewhere in your PATH
  - On 64bit Mac OS X download the client from [here](https://get.docker.com/builds/Darwin/x86_64/docker-1.6.2), rename it to **docker**, make it executable  and put it somewhere in your PATH 
- Cloud Foundry CLI 6.11.3 or later
   - If you already have the Cloud Foundry CLI verify the version is at least 6.11.3 via the `cf -v` command. If you need to install it get the appropriate one for your platform from [here] (https://github.com/cloudfoundry/cli/releases)
- IBM Containers plug-in for Cloud Foundry
   - Follow the instructions for setting up the IBM Containers Plugin for  Cloud Foundry [here] (https://www.ng.bluemix.net/docs/containers/container_cli_cfic.html#container_cli_cfic)   
- Verify you can login into Bluemix and to IBM Containers from the command line  with the following sequence of commands:
```sh
  cf login
  cf ic login
```
- Setup the unique path to your private IBM Containers repository
   - In the Bluemix dashboard at (http://bluemix.net) click on **START CONTAINERS**. If you've never used IBM Containers before you'll be prompted to provide a unique suffix for your private image repository.
- Build the image in your private repository 
  - Back on the command line,   issue the following command   (note replace *foobar* with the unique suffix to your private repository)
```sh
   cf ic build -t registry.ng.bluemix.net/foobar/bluemix-hue-filebrowser github.com/ibmecod/bluemix-hue-filebrowser
```
*Note: This will take a few minutes because building  HUE from source takes a while *

## Running the HUE file browser image in the IBM Bluemix Containers environment

### 1. Create a Bluemix app with the IBM Analytics for Apache Hadoop Service

  1. *Note: If you have an existing Bluemix app that you want to bind  to  the Analytics for Apache Hadoop Service,  skip to Step 7.*  In the Bluemix dashboard click on **CREATE APP**
  2. Click on **Web**
  3. Click on **SDK for Node.js**
  4. Click on **CONTINUE**
  5. Give the app a system wide unique name and click **FINISH**
  6. When the message indicates that your app has started, click on the **Back to Dashboard** link 
  7. Under **Applications** click on your application's rectangle
  8. Click on **ADD A SERVICE OR API**, and then scroll down to the **Data & Analytics** section
  9. Click on **Analytics for Apache Hadoop** and then click **CREATE**
  10. Click on **RESTAGE** when prompted.  When the message indicates that your app has restarted, click on the **Back to Dashboard** link 

### 2. Create a running instance of the Docker image
  1. In the Bluemix dashboard click on **START CONTAINERS**
  2. Click on the icon for the *hue-filebrowser-bluemix* image
  3. Give the container a name and select **Request and Bind Public IP** under **Public IP Address**
  4. Enter *8000* under **Public Ports**
  5. Expand **Advanced Options** and select the app you created in the previous section under **Service Binding**
  6. Click **CREATE** and wait until the container shows as being started
  7. Note the Public IP assigned to the container once it has been started and make sure it's been mapped to the app bound to your instance of the IBM Analytics for Apache Hadoop Service
  
   ![hue filebrowser screenshot](/screenshots/runningcontainer.png)

### 3. Running the HUE File Browser
  1. Enter the URL *[Container IP]:8000/filebrowser* where *[Container IP]* is the IP bound  to the  container. For example if the IP is *136.168.88.76* the URL would be *http://136.168.88.76:8000/filebrowser* 
  2. Enter `hue` as the username (note no password is required and any username will do )
  3. Verify that you're able to navigate through the HDFS file system on your instance of IBM Analytics for Apache Hadoop Service. You'll have the permissions of the username specified in the service's meta data 
     
     ![hue filebrowser screenshot](/screenshots/filebrowser.png)
	 
	 
## Running the HUE file browser image in another Docker environment 

### 1. Build the image
   1.  In the other Docker environment run the command
```sh
   docker build -t your_tag_name github.com/ibmecod/bluemix-hue-filebrowser
```

### 2. Create a Bluemix app with the IBM Analytics for Apache Hadoop Service
   1. Follow the  instructions in step 1 of the  previous section 

### 3. Get the Service instance credentials
  1. In the Bluemix Dashboard under **Applications** click on your application's rectangle
  2. Scroll down to the bound Analytics for Apache Hadoop Service and click on **Show Credentials** 
  3. Note the values of the username, password and WebHDFS URL
  
### 4. Run the Docker image
  1. Run the Docker image with the following env vars set to the service credentials noted 
     - *WEBHDFS_USER* set to the username from the  service credentials 
	 - *WEBHDFS_PASSWORD* set to  the password from the service credentials 
	 - *WEBHDFS_URL* set to the WebHDFS URL from  the service credentials
 
### 5. Run the HUE File Browser 
   1. Follow  Step 3 in the previous section using the appropriate IP Address for  the Docker daemon  and the port that is mapped to port 8000 of the running image
   
## Troubleshooting 
The HUE filebrowser will not start if the credentials for the Analytics for Apache Hadoop Service are not discoverable via VCAP_SERVICES or the alternative env vars noted the previous section.

If you're unable to access the URL of the running container that is the most likely cause.

The command `cf ic logs container_name` will give you access to the logs of the running container.

If the service credentials are found (in VCAP_SERVICES or the alternate  env vars) the log will contain something similar to the following:
```sh
Validating models...

0 errors found
July 25, 2015  - 14:45:48 
Django version 1.6.10, using settings 'desktop.settings'
Starting the development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```
If your logs look like this and the app isn't showing up in your browser:
 - Make sure a public  IP address is mapped to the running container
 - If it is mapped you may have to wait a couple of minutes because the public IP mapping  in IBM Containers may not always be instantaneous. Wait a  couple of minutes and try again.

If your service credentials are not found the logs  will look like the following 
```sh
Fatal error: cannot find Web HDFS credentials and/or endpoint
```
If your logs look like this then delete the running container and recreate it  making sure to map it to an app that is bound to an instance of the Analytics for Apache Hadoop Service


## Modifications made to original HUE 3.8.1 source code
[../hue-3.8.1-bluemix/desktop/core/src/desktop/conf.py](https://raw.githubusercontent.com/ibmecod/bluemix-hue-filebrowser/master/hue-3.8.1-bluemix/desktop/core/src/desktop/conf.py)
Added another config object available via hue.ini that contains the password needed for Basic Authentication against the WebHDFS endpoint

[../hue-3.8.1-bluemix/desktop/core/src/desktop/auth/views.py](https://raw.githubusercontent.com/ibmecod/bluemix-hue-filebrowser/master/hue-3.8.1-bluemix/desktop/core/src/desktop/auth/views.py)
Commented out code that assumes the hue user is the hdfs user since the user is taken from the Service's VCAP_SERVICES data

[../hue-3.8.1-bluemix/desktop/libs/hadoop/src/hadoop/fs/webhdfs.py](https://raw.githubusercontent.com/ibmecod/bluemix-hue-filebrowser/master/hue-3.8.1-bluemix/desktop/libs/hadoop/src/hadoop/fs/webhdfs.py)
Modified code that accesses the WebHDFS URL to use Basic Authentication

