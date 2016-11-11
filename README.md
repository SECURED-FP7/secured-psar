


# Introduction
This project describes how to install and deploy a local all-in-one PSAR based in OpenStack IceHouse Version and OpenMANO. Recent releases of OpenStack could be compatible but have not been tested.

What kind of backend to use is configurable during the installation. It is not recommended to switch the backend (OpenStack/OpenMANO) once you have started to store information. If it is needed then you must migrate the information manually.

Next Figure shows the internals of PSAR. 
![PSA Repository](images/PSAR_repository.png)

## Openstack Backend

It is compound of:

**Keystone** module will be used to offer a Authentication and authorization module for the infrastructure on PSAR, but also can be offered for other elements.

**Glance** module will offer a repository for Virtual Machines images and also plugins code

**Swift** module allows to store PSA manifest XML file.

All Open Stack modules are invoked via Manager module using different Open Stack API. This modularity allows switching to others models of storage.

One of the great advantages of use Open Stack is that allows integration and visualization of PSAs through external systems. The simplest case is accessing via a Horizon module.


## OpenMANO Backend
It is compound of:

**Keystone** module will be used to offer a Authentication and authorization module for the infrastructure on PSAR, but also can be offered for other elements.

**Local Storage** allows to store in local files some information, like manifest or plugin.

**OpenMANO** is an open source project that provides a practical implementation of the reference architecture for Management & Orchestration under standardization at ETSI’s NFV ISG (NFV MANO). It consists of three main SW components:

* **openvim**: reference implementation of an NFV VIM (Virtualised Infrastructure Manager). It interfaces with the compute nodes in the NFV Infrastructure and an openflow controller in order to provide computing and networking capabilities and to deploy virtual machines. 

* **openmano**: reference implementation of an NFV-O (Network Functions Virtualisation Orchestrator).

* **openmano-gui**: web GUI to interact with openmano server, through its northbound API, in a friendly way.


This tutorial was tested using a server running Ubuntu 14.04 LTS

# Repository content:

The list folders includes:

* PSA - Manager module of PSAR. 
* client - Developed to be used by other components to interact with PSAR API. Includes a python module to be used and some CLI clients in python.
* images - Auxiliary images for documentation
* psar - Django framework. Auxiliary files
* tests - Unitary testing scripts
* v1status - Django framework. Auxiliary files


# Installing and configuring openstack:

Default version for Openstack on the Ubuntu 14.04 repositories is Icehouse. Availability of the packages is guaranteed until 14.04 EOL, but no updates are available from Openstack. Details in <https://wiki.ubuntu.com/ServerTeam/CloudArchive>

Newer versions than Icehouse are not tested, and may require additional configuration
	
## Keystone:

Start with keystone, as the other two make use of its authentication services

### Installation:

*	Install keystone and mysql (do not forget to define root password) from the Ubuntu Repositories

		sudo apt-get install keystone mysql-server python-mysqldb		

*	Edit /etc/keystone/keystone.conf and change the [database] section. Replace KEYSTONE_DBPASS with a suitable password for the database user:

			[database]
			# The SQLAlchemy connection string used to connect to the database
			connection = mysql://keystone:KEYSTONE_DBPASS@127.0.0.1/keystone

*       Restart Keystone to apply the changes:

                        sudo service keystone restart

	If previous command fails to start keystone, alternatives (sudo service keystone stop; sudo keystone-all &)


*	Create a keystone database user:

			$ mysql -u root -p
				mysql> CREATE DATABASE keystone;
				mysql> GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'localhost' \
					IDENTIFIED BY 'KEYSTONE_DBPASS';
				mysql> GRANT ALL PRIVILEGES ON keystone.* TO 'keystone'@'%' \
						IDENTIFIED BY 'KEYSTONE_DBPASS';
				mysql> exit
			
*	And the tables:

			sudo keystone-manage db_sync

*	Edit /etc/keystone/keystone.conf and change the [DEFAULT] section, replacing ADMIN_TOKEN with a random token (e.g. generate with "openssl rand -hex 10"):

			[DEFAULT]
			# A "shared secret" between keystone and other openstack services
			admin_token = ADMIN_TOKEN	

*	Configure the log directory. Edit the /etc/keystone/keystone.conf file and update the [DEFAULT] section:

			[DEFAULT]
			...
			log_dir = /var/log/keystone
			

*	Run the following command:
			
			sudo keystone-manage pki_setup --keystone-group=keystone --keystone-user=keystone
			
*	Restart Keystone service:

			sudo service keystone restart

### Creating tenants, users and services:

*	Until we create an admin profile, we need to bypass the authentication system. To do that:
	
			export OS_SERVICE_TOKEN=ADMIN_TOKEN
			export OS_SERVICE_ENDPOINT=http://YOUR_IP:35357/v2.0

*	First, we create the admin user:
	
			keystone user-create --name=admin --pass=ADMIN_PASS

*	Then, the tenant:

			keystone tenant-create --name=admin --description="Admin Tenant"

*	And the role:
	
			keystone role-create --name=admin
		
*	Then link them together:
	
			keystone user-role-add --user=admin --tenant=admin --role=admin

*	And with the  _member_ role
	
			keystone user-role-add --user=admin --role=_member_ --tenant=admin
	
*	Create a service tenant:
		
			keystone tenant-create --name=service --description="Service Tenant"
	
### Create services and endpoints:
			
*	Create the identity service:

			keystone service-create --name=keystone --type=identity \
					--description="OpenStack Identity"

*	Specify an API endpoint:

			keystone endpoint-create  --service-id=$(keystone service-list | awk '/ identity / {print $2}') \
					--publicurl=http://YOUR_IP:5000/v2.0 --internalurl=http://YOUR_IP:5000/v2.0 \
					--adminurl=http://YOUR_IP:35357/v2.0
	
### Verify installation and configuration:

*	Now there is no need to bypass the authentication system, so	

			unset OS_SERVICE_TOKEN OS_SERVICE_ENDPOINT

*	Run the following command:
				
			keystone --os-username=admin --os-password=ADMIN_PASS --os-auth-url=http://YOUR_IP:35357/v2.0 token-get
	
*	If it returns an authentication token, then the service is running
	
	*	If it returns a error message 
			
			Authorization Failed: An unexpected error prevented the server from fulfilling your request. (HTTP 500)

One solution that worked was to stop the keystone service, then starting it manually

		sudo service keystone stop
		sudo keystone-all &

*	Now set enviromental variables so there is no need of specifying all the arguments in following commands
		
		export OS_USERNAME=admin
		export OS_PASSWORD=ADMIN_PASS
		export OS_AUTH_URL=http://YOUR_IP:35357/v2.0
		export OS_TENANT_NAME=admin
			
## Glance:
Note: Install only if you are going to use it as a backend.
*	Install glance from the repositories

		sudo apt-get install glance glance-common

*	Edit /etc/glance/glance-api.conf and /etc/glance/glance-registry.conf and edit the [database] section of each file:

			[database]
			connection = mysql://glance:GLANCE_DBPASS@127.0.0.1/glance
	
*	Restart Glance: 

		sudo service glance-api restart
		sudo service glance-registry restart

*	Create the database:
	
			mysql -u root -p
				mysql> CREATE DATABASE glance;
				mysql> GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'localhost' \
					IDENTIFIED BY 'GLANCE_DBPASS';
				mysql> GRANT ALL PRIVILEGES ON glance.* TO 'glance'@'%' \
					IDENTIFIED BY 'GLANCE_DBPASS';
				mysql> exit

*	And the tables:
	
			sudo glance-manage db_sync

It is posible that you receive an error stating that "Tables "migrate_version" have non utf8 collation, please make sure all tables are CHARSET=utf8". In that case, run the following commands:
		
		mysql -u root -p glance
			mysql> alter table migrate_version convert to character set utf8 collate utf8_unicode_ci;
			mysql> flush privileges;
			mysql> quit

And try to synchronize the database again 

*	Create a glance user on the identity service:

			keystone user-create --name=glance --pass=GLANCE_PASS --email=glance@example.com
			keystone user-role-add --user=glance --tenant=service --role=admin
	
*	Edit the /etc/glance/glance-api.conf and /etc/glance/glance-registry.conf files. 

	*	Replace GLANCE_PASS with the password you chose for the glance user in the Identity service.

	*	Add or modify the following keys under the [keystone_authtoken] section:

				[keystone_authtoken]
				auth_uri = http://YOUR_IP:5000
				auth_host = YOUR_IP
				auth_port = 35357
				auth_protocol = http
				admin_tenant_name = service
				admin_user = glance
				admin_password = GLANCE_PASS

Heads-up: To avoid problems when parsing this keys, it is recommended to manually write them instead of copy from the manual and paste on the file  


*	Modify the following key under the [paste_deploy] section:
		
			[paste_deploy]
			...
			flavor = keystone
			
*	Register the service and create the endpoint:
			
			keystone service-create --name=glance --type=image --description="OpenStack Image Service"
			keystone endpoint-create --service-id=$(keystone service-list | awk '/ image / {print $2}') \
				--publicurl=http://YOUR_IP:9292 --internalurl=http://YOUR_IP:9292 --adminurl=http://YOUR_IP:9292
					
					
*	Restart the service with the new configuration:
	
			sudo service glance-registry restart
			sudo service glance-api restart
	
### Verify the installation

*	Download a test image, e.g.:

		mkdir /tmp/images
		cd /tmp/images/
		wget https://launchpadlibrarian.net/83303699/cirros-0.3.0-i386-disk.img
		
*	And upload it with the generic command:

		glance image-create --name=IMAGELABEL --disk-format=FILEFORMAT --container-format=CONTAINERFORMAT --is-public=ACCESSVALUE < IMAGEFILE

Where:

IMAGELABEL: Arbitrary label. The name by which users refer to the image.

FILEFORMAT: Specifies the format of the image file. Valid formats include qcow2, raw, vhd, vmdk, vdi, iso, aki, ari, and ami. You can verify the format using the file command:
		
		file cirros-0.3.0-i386-disk.img
		cirros-0.3.0-i386-disk.img: QEMU QCOW Image (v2), 41126400 bytes

CONTAINERFORMAT: Specifies the container format. Valid formats include: bare, ovf, aki, ari and ami. Although this field is currently required, it is not actually used by any of the OpenStack services and has no effect on system behavior. Because the value is not used anywhere, it is safe to always specify bare as the container format.

ACCESSVALUE: Specifies image access: true - All users can view and use the image. false - Only administrators can view and use the image.

IMAGEFILE: Specifies the name of your downloaded image file.

Example:
		glance image-create --name=TestImage --disk-format=qcow2 --container-format=bare --is-public=true < /tmp/images/cirros-0.3.0-i386-disk.img


## Swift (All-in-one installation):
Note: Install only if you are going to use it as a backend.
	
Swift requires a little more work to do than the previous two. Since we are deploying it in a single machine, we need to make an all-in-one installation. We could not make Keystone authentication work in this case, so we are using v1 authentication

Much of the configuration described in this guide requires escalated administrator (root) privileges; however, we assume that administrator logs in as an unprivileged user and can use sudo to run privileged commands.

Swift processes also run under a separate user and group, set by configuration option, and referenced as \<your-user-name\>:\<your-group-name\>. The default user is swift, which may not exist on your system. These instructions are intended to allow a developer to use his/her username for \<your-user-name\>:\<your-group-name\>.
			
**We are using a loopback device as a storage system.** 
			
*	Install dependencies:
		
		sudo apt-get update
		sudo apt-get install curl gcc memcached rsync sqlite3 xfsprogs \
                     git-core libffi-dev python-setuptools
		sudo apt-get install python-coverage python-dev python-nose \
                     python-simplejson python-xattr python-eventlet \
                     python-greenlet python-pastedeploy \
                     python-netifaces python-pip python-dnspython \
                     python-mock python-swiftclient
			
*	Create the device:

			sudo mkdir /srv
			sudo truncate -s 1GB /srv/swift-disk
			sudo mkfs.xfs /srv/swift-disk

*	Edit /etc/fstab and append at the end:
		
		/srv/swift-disk /mnt/sdb1 xfs loop,noatime,nodiratime,nobarrier,logbufs=8 0 0
	
*	Create the mount point and the individualized links:
		
			sudo mkdir /mnt/sdb1
			sudo mount /mnt/sdb1
			sudo mkdir /mnt/sdb1/1 /mnt/sdb1/2 /mnt/sdb1/3 /mnt/sdb1/4
			sudo chown ${USER}:${USER} /mnt/sdb1/*
			for x in {1..4}; do sudo ln -s /mnt/sdb1/$x /srv/$x; done
			sudo mkdir -p /srv/1/node/sdb1 /srv/2/node/sdb2 /srv/3/node/sdb3 /srv/4/node/sdb4 /var/run/swift
			sudo chown -R ${USER}:${USER} /var/run/swift
			# **Make sure to include the trailing slash after /srv/$x/**
			for x in {1..4}; do sudo chown -R ${USER}:${USER} /srv/$x/; done

*	Add the following lines to /etc/rc.local before the exit 0 (Remember to change your user and group names!):
		
			mkdir -p /var/cache/swift /var/cache/swift2 /var/cache/swift3 /var/cache/swift4
			sudo chown <your-user-name>:<your-group-name> /var/cache/swift*
			mkdir -p /var/run/swift
			chown <your-user-name>:<your-group-name> /var/run/swift
			
*	Check out the source code of swift from the git repository (following instructions will suppose you downloaded it in your home directory)
		
			cd ~
			git clone https://github.com/openstack/swift.git
			
*	Build a development installation of swift:
		
			sudo pip install PyECLib six eventlet --upgrade
			cd $HOME/swift; sudo python setup.py develop; cd -
	
	Only if previous step failed for python version on six and eventlet, try to install manually:
			
		wget https://pypi.python.org/packages/source/s/six/six-1.9.0.tar.gz#md5=476881ef4012262dfc8adc645ee786c4
    			tar -zxvf six-1.9.0.tar.gz
    			cd six-1.9.0
    			sudo python setup.py install
    			cd -

	Only if previous step failed for python version on PyECLib with <erasurecode.h>, try:
        
            sudo apt-get install liberasurecode-dev
            sudo pip install -I PyECLib==1.0.7
            sudo ldconfig

*	Install swifts test dependencies:
		
			sudo pip install -r $HOME/swift/test-requirements.txt

*	Create /etc/rsyncd.conf:

			sudo cp $HOME/swift/doc/saio/rsyncd.conf /etc/
			sudo sed -i "s/<your-user-name>/${USER}/" /etc/rsyncd.conf 

*	On Ubuntu, edit the following line in /etc/default/rsync:
			
			RSYNC_ENABLE=true
	
*	Start the rsync daemon. On Ubuntu, run:
		
			sudo service rsync restart
	
*	Verify rsync is accepting connections for all servers:
			
			rsync rsync://pub@localhost/
			
It should show something like this:

			account6012
			account6022
			account6032
			account6042
			container6011
			container6021
			container6031
			container6041
			object6010
			object6020
			object6030
			object6040


*	Configure each node:
			
	*	Optionally remove an existing swift directory:
			
				sudo rm -rf /etc/swift
	
	*	Populate the /etc/swift directory itself:
			
				cd $HOME/swift/doc; sudo cp -r saio/swift /etc/swift; cd -
				sudo chown -R ${USER}:${USER} /etc/swift
	
	*	Update <your-user-name> references in the Swift config files:
	
				find /etc/swift/ -name \*.conf | xargs sudo sed -i "s/<your-user-name>/${USER}/"

 Following list shows modified files by previous command:

			/etc/swift/proxy-server.conf 
			/etc/swift/object-expirer.conf
			/etc/swift/container-reconciler.conf
			/etc/swift/account-server/1.conf
			/etc/swift/container-server/1.conf
			/etc/swift/object-server/1.conf
			/etc/swift/account-server/2.conf
			/etc/swift/container-server/2.conf
			/etc/swift/object-server/2.conf
			/etc/swift/account-server/3.conf
			/etc/swift/container-server/3.conf
			/etc/swift/object-server/3.conf
			/etc/swift/account-server/4.conf
			/etc/swift/container-server/4.conf
			/etc/swift/object-server/4.conf
				
*	Copy the SAIO scripts for resetting the environment:	

			cd $HOME/swift/doc; cp -r saio/bin $HOME/bin; cd -
			chmod +x $HOME/bin/*
				
*	Since we are using a loopback device, add an environment var to subsitute /dev/sdb1 with /srv/swift-disk on the $HOME/bin/resetswift script:
	
			echo "export SAIO_BLOCK_DEVICE=/srv/swift-disk" >> $HOME/.bashrc
			
*	Install the sample configuration file for running tests:
	
			cp $HOME/swift/test/sample.conf /etc/swift/test.conf
				
*	Add an environment variable for running tests below:

			echo "export SWIFT_TEST_CONFIG_FILE=/etc/swift/test.conf" >> $HOME/.bashrc

*	Be sure that your PATH includes the bin directory:

			echo "export PATH=${PATH}:$HOME/bin" >> $HOME/.bashrc
	
*	Source the above environment variables into your current environment:
		
			. $HOME/.bashrc
				
*	Construct the initial rings using the provided script:
	
			remakerings
		
*	Start the main" Swift daemon processes (proxy, account, container, and object):
	
			swift-init main start

### Testing:	

*	Verify the funtional tests run (ignore test_cross_policy Errors):
	
			$HOME/swift/.functests

*	Verify the probe tests run:

			$HOME/swift/.probetests

*	Check that swift works correctly:
			
				
			swift -A http://127.0.0.1:8080/auth/v1.0 -U test:tester -K testing post container2
			echo "Everything OK" > test.txt 
			swift -A http://127.0.0.1:8080/auth/v1.0 -U test:tester -K testing upload container2 test.txt
			rm test.txt 
			swift -A http://127.0.0.1:8080/auth/v1.0 -U test:tester -K testing download container2 test.txt
			cat test.txt

### Container Creation:

If previous test has been done with other container name, create the container for the service:

			swift -A http://127.0.0.1:8080/auth/v1.0 -U test:tester -K testing post container2
 
	
# Preparing Django Server:

Clone the repository into a new directory (i.e. git) and create a django project in another directory (i.e. psar)

		sudo apt-get install libssl-dev libmysqlclient-dev python-virtualenv screen
		mkdir $HOME/git
		cd $HOME/git
		#Choose protocol and credentials for clone, git:// or https:// 
		git clone https://gitlab.secured-fp7.eu/secured/psar.git
		cd $HOME
                virtualenv .env
                source .env/bin/activate
                pip install django djangorestframework MySQL-python python-keystoneclient python-glanceclient python-swiftclient django-rest-swagger wrapt
                mkdir psar
		django-admin.py startproject psar psar
		cp -r git/psar/* psar/
                cd psar


By default, when you use the api you don't have to specify an auth token provided by keystone. These tokens can be very long and will make the use of the api a bit complicated. If you want to enable the token authentication, just change

		auth=False

For

		auth=True
		
In v1Status/views.py and PSA/constants.py

Create the database (choose your own DB_USER and DB_PASS):
	
		mysql -u root -p
			mysql> CREATE DATABASE PSAR;
			mysql> GRANT ALL PRIVILEGES ON PSAR.* TO 'DB_USER'@'localhost' \
				IDENTIFIED BY 'DB_PASS';
			mysql> GRANT ALL PRIVILEGES ON PSAR.* TO 'DB_USER'@'%' \
				IDENTIFIED BY 'DB_PASS';
			mysql> exit

Modify the database information on psar/PSA/settings.py (replace DB_USER and DB_PASS with previous chosen values) :

		DATABASES = {
 		   'default': {

		        'ENGINE': 'django.db.backends.mysql',
       			'NAME':'PSAR',
        		'USER': os.getenv('DATABASE_USER','DB_USER'),
        		'PASSWORD': os.getenv('DATABASE_PASS', 'DB_PASS'),	
			'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
        		'PORT': '3306',
    			}
		}

	
Synchronize the database

		python manage.py makemigrations
		python manage.py migrate
		
#admin Running the server:
Before running the server, check if all the openstack services are running. If not, start them:

		sudo service keystone start
	 	sudo service glance-registry start
                sudo service glance-api start	
		sudo swift-init main start

Modify the default values on PSA/constants.py, in particular:
*	The IP address of your PSAR ('your_ip' in YOUR_IP )
*	OpenStack credentials ( 'admin'  in ADMIN_USER, ADMIN_PASS and TENANT_NAME)
*	Token based authentication ( False in auth)

		YOUR_IP = os.getenv('YOUR_IP', 'your_ip')
		ADMIN_USER = os.getenv('OS_USERNAME','admin')
		ADMIN_PASS = os.getenv('OS_PASSWORD', 'admin')
		TENANT_NAME= os.getenv('OS_TENANT_NAME','admin')
		auth=os.getenv('PSAR_AUTH_ON',False)

Alternatively, you can define environment variables for all this values before starting the server.

		export YOUR_IP=your_ip
		export OS_USERNAME=admin
		export OS_PASSWORD=admin
		export OS_TENANT_NAME=admin
		export PSAR_AUTH_ON=True
		


Now you can run the server (make sure you have virtualenv active) and YOUR_IP must be real IP address:
		
		python manage.py runserver YOUR_IP:8080
		
If you want to run in background use screen application:
		screen -S PSAR
		source .env/bin/activate
		cd $HOME/psar
		python manage.py runserver YOUR_IP:8080

Leave running the session with Ctrl+a+d


Now you can access the api, according to the documentation. 

You can access to the API reference using the URL http://YOUR_IP:8080/docs/

# Update documentation page:

To show a SECURED-themed documentation page, copy the files in the directory "change_doc" in the corresponding place:

	base.html -> .env/lib/python2.7/site-packages/rest_framework_swagger/templates/rest_framework_swagger/base.html
	logo_small.png -> .env/lib/python2.7/site-packages/rest_framework_swagger/static/rest_framework_swagger/images/logo_small.png
	screen.css -> .env/lib/python2.7/site-packages/rest_framework_swagger/static/rest_framework_swagger/css/screen.css
	rest_framework_swagger.css -> .env/lib/python2.7/site-packages/rest_framework_swagger/static/rest_framework_swagger/css/rest_framework_swagger.css


# Securing the server:
If you want to access the server through https (thus encrypting the petitions and responses), you have to install nginx
	
		sudo apt-get install nginx
		
Now, you have to create a certificate for the server. In this guide we are using a self signed certificate.

First, generate a server key:
		
		openssl genrsa -des3 -out psar.key 2048

You will have to enter a password for the key  
		
Now, generate a Certificate Signing Request:
		
		openssl req -new -key psar.key -out psar.csr
		
You will be asked some infomation (Organization name, country...). It's important that the Common Name is the IP and port in which the server will be running

Now, sign the certificate:

	openssl x509 -req -days 365 -in psar.csr -signkey psar.key -out psar.crt
	
Finally, create a version of the key that doesn't require password:

	openssl rsa -in psar.key -out psar.key.insecure
	mv psar.key psar.key.secure
	mv psar.key.insecure psar.key
	
You will have to pass the certificate (psar.crt) to the clients, and add it to the list of trusted certificates in the clients machine. The exact commands depend on the OS of the machine.

The nginx.conf file contains the configuration needed to run the PSAR in https mode, but you will need to modify it to work: Replace YOUR_IP with the IP of the server, and specify the absolute route to the certificat, key and static folder (the server's folder +'/static') 

Once the file is ready, copy it to its location:

	sudo cp nginx.conf /etc/nginx/sites-enabled/psar

And restart nginx:

	sudo /etc/init.d/nginx restart

Run this command to collect all static files, needed for the documentation:

	python manage.py collectstatic

Now you will have to run an instance of the UPR listening on 127.0.0.1:8888 :

	python manage.py runserver 127.0.0.1:8888

While this instance is running, you will have access to the API via HTTPS using the IP and port defined in nginx.conf
	
If you want to run in background use screen application:

		screen -S PSAR
		source .env/bin/activate
		cd $HOME/psar
		python manage.py runserver 127.0.0.1:8888 

Leave running the session with Ctrl+a+d



# Installing and configuring OpenMANO

This additional installation steps are needed only if you are going to use OpenMANO as backend.

### Installing and configuring Openmano:

Use the next guide for do the automatic installation, and  configuration.
 
[OpenMANO Getting Started](https://github.com/nfvlabs/openmano/wiki/Getting-started)

#### Openvim

Actions related to the infrastructure must be conveyed through the openvim client.

Let's configure the openvim CLI client. Needed if you have changed the openvimd.cfg file

	./openvim config                           # show openvim related variables

	#To change variables run
	export OPENVIM_HOST=<http_host of openvimd.cfg>
	export OPENVIM_PORT=<http_port of openvimd.cfg>
	export OPENVIM_ADMIN_PORT=<http_admin_port of openvimd.cfg>

	#You can insert at .bashrc for authomatic loading at login:
	echo "export OPENVIM_HOST=<...>" >> /home/${USER}/.bashrc
	...
Let's attach compute nodes. For choose the mode, you need change the file **$HOME_OPENMANO/openmano/openvim/openvimd.cfg**. We use 'test' mode.

In 'test' mode we need to provide fake compute nodes with all the necessary information:

  	./openvim host-add test/hosts/host-example0.json 
  	./openvim host-add test/hosts/host-example1.json 
  	./openvim host-add test/hosts/host-example2.json 
  	./openvim host-add test/hosts/host-example3.json 
  	./openvim host-list                        #-v,-vv,-vvv for verbosity levels


Let's list the external networks:

 	./openvim net-list

Let's create some external networks in openvim. These networks are public and can be used by any VNF. It must be noticed that these networks must be pre-provisioned in the compute nodes in order to be effectively used by the VNFs. The pre-provision will be skipped since we are in test mode. Four networks will be created:

* default -> default NAT network provided by libvirt. By creating this network, VMs will be able to connect to default network in the same host where they are deployed.

#
 	./openvim net-create test/networks/net-example0.yaml

Let's list the external networks:

 	./openvim net-list
 	35671f9e-e2b4-11e4-a3c9-52540032c4fa   default
 
	

Now let's create a new tenant "admin":

	$ openvim tenant-create
	tenant name? admin
	tenant description (admin)?
	<uuid>   admin   Created
Take the uuid of the tenant and update the environment variables associated to the openvim tenant:

	export OPENVIM_TENANT=<obtained uuid>
	#echo "export OPENVIM_TENANT=<obtained uuid>" >> /home/${USER}/.bashrc
	openvim config                             #show openvim env variables


#### Openmano
Let's configure the openmano CLI client. This is only necessary if you have changed the file 'openmanod.cfg'

* Create a directory from images. 

		mkdir $HOME/images
If you want use other directory from PSA images you can change pathMano in **'/psar/psar.conf'**


* List the environment variables

        ./openmano config                      #show openmano env variables

* Update the environment variables accordingly:

        export OPENMANO_HOST=<http_host of openmanod.cfg>
        export OPENMANO_PORT=<http_port of openmanod.cfg>
        ./openmano config                      #show openmano env variables

* Let's create a new tenant:

        ./openmano tenant-create mytenant --description=tenant-description
        ./openmano tenant-list                           #show list of tenants uuid and name

* Take the uuid and update the environment variable associated to the openmano tenant:

        export OPENMANO_TENANT=<obtained uuid> 
        ./openmano config                                #show openmano env variables

* Let's create a new datacenter 'mydc' in openmano, attach the datacenter 'mydc' and VIM tenant "admin" (identified by its uuid provided by openvim), and update the external nets automatically from the ones in openvim.

		./openmano datacenter-create mydc http://localhost:9080/openvim
		./openmano datacenter-list --all                           #show all datacenters
		./openmano datacenter-attach mydc --vim-tenant-id <uuid>   #attach the datacenter mydc and openvim tenant id to the openmano tenant 'mytenant'
		./openmano datacenter-list                                 #show datacenters associated to our tenant
		./openmano datacenter-net-update mydc
 		Edit datacenter mydc (y/N)? y
		35671f9e-e2b4-11e4-a3c9-52540032c4fa   default
		./openmano datacenter-net-list mydc
		35671f9e-e2b4-11e4-a3c9-52540032c4fa   default              2015-04-14T17:36:32

#### Openmano-gui

First, edit and configure the ./openmano-gui/config.php file. It is needed to get the tenant added at openmano in the previous step and set the $mano_tenant variable properly. In case of using a different configuration than the explained above, it is needed to modify other variables.

openmano-gui is accesible with url http://server/openmano. It contain three main modules:

* Scenarios. Left side: scenario and instance scenario list. Right side: scenario/instance details of the left side selected element. The upper button allows:
    * New: To create a new scenario dragging and drop the left VNF/nets catalogue. You can connect the VNF interfaces among them with the mouse. Do not forget to save.
    * Action over the left side selected scenario, as Save its topology changes, Deploy it, Clone in order to create a new one using the current scenario as starting point, Delete, ...
    * Action over left side selected instance-scenario, as Update to see the current status of running VNFs, Delete to undeploy the instance, Start, Shutdown, Force off, Reboot, Rebuild over selected VNFs or/and VMs of the instance, ...
* VNFs. Left side: list of VNF and external nets. Right side: under construction
* Physical. Left side: list of openvim compute nodes and deployed virtual machines. Right side: under construction


### In the Django Server:

* Update the server
    * If you are already running a PSAR instance, access to the virtual environment where you are running it, stop and install additional packages:

    		screen -x PSAR
    		Ctrl+c (Kill server)
    		pip install paramiko
    		pip install argcomplete
    		
    * If it is the first time, create a background session and install additional packages:
    
    		screen -S PSAR
    		source .env/bin/activate
    		cd $HOME/psar
    		pip install paramiko
    		pip install argcomplete



* Replace 'obtained uuid', 'Openmano ip', 'Openmano port', 'Openmano user', 'Openmano pass', '$HOME_OPENMANO' and '$HOME'

		[mano]
		tenant = obtained uuid
		ipMano = Openmano ip
		portMano = Openmano port
		userMano = Openmano user
		passMano = Openmano pass

		pathMano = $HOME_OPENMANO/images/
		vnfrepo= $HOME_OPENMANO/openmano/openmano/vnfrepo/
		pathlocalpsar=$HOME/psar/
		pathfiles= $HOME/psar/files/
		pathYamlVnf=$HOME/psar/VNFrepo/

* Default path for manifest and plugin is 'pathfiles=$HOME/psar/files', and for VNFs repository is 'pathfiles=$HOME/psar/VNFrepo', you need to  create them (or the ones choosen):

		mkdir $HOME/psar/files
		mkdir $HOME/psar/VNFrepo

* Modify the default values on **psar/psar.conf** With this variable you can configure use OPENMANO instead of default OPENSTACK value:

		[repository]
		repository = OPENMANO

* Restart the instance of PSAR

    
		screen -x PSAR
		cd $HOME/psar
		python manage.py runserver 127.0.0.1:8888 

Leave running the session with Ctrl+a+d






# Maintenance: Clear PSAR database content

This steps perform a hard reset of the PSAR database, removing a existing DB and creating a new empty one 

1.Stop the PSAR Server.

    $screen -x psar
    $Ctrl+C
2.Delete and Re-create the database:
First if exist remove "/psar/PSA/migrations" directory. 

		mysql -u root -p
		    mysql> DROP DATABASE PSAR;
			mysql> CREATE DATABASE PSAR;
			mysql> GRANT ALL PRIVILEGES ON PSAR.* TO 'DATABASE_USER'@'localhost'IDENTIFIED BY 'DATABASE_PASS';
			mysql> GRANT ALL PRIVILEGES ON PSAR.* TO 'DATABASE_USER'@'%' IDENTIFIED BY 'DATABASE_PASS';
			mysql> exit



3.Regenerate empty database schema:

        $cd $HOME
        $source env_psar/bin/activate
        $cd psar
        $python manage.py makemigrations PSA
        $python manage.py migrate


4.Start the UPR

        $cd $HOME
        $screen -S psar
        $source start_psar.sh
        Ctrl+a+d



# References:


*	<http://www.django-rest-framework.org/tutorial/quickstart/>
*	<http://docs.openstack.org/icehouse/install-guide/install/apt/content/index.html>	
*	<http://docs.openstack.org/developer/swift/development_saio.html>
*	<https://github.com/nfvlabs/openmano/>

