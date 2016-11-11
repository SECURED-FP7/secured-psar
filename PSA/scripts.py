from subprocess import call
from keystoneclient.v2_0 import client
import swiftclient
import json
from keystoneclient.auth.identity import v2 as identity
from keystoneclient import session
from glanceclient import Client
import uuid, hashlib, os, logging
from django.core.exceptions import ObjectDoesNotExist
from ConfigParser import SafeConfigParser



parser = SafeConfigParser()
parser.read('psar.conf')
logging.basicConfig(filename=parser.get('logging','filename'),format='%(asctime)s %(levelname)s:%(message)s', level=parser.get('logging','level'))


YOUR_IP = os.getenv('YOUR_IP', parser.get('General','YOUR_IP'))

ADMIN_USER = os.getenv('OS_USERNAME',parser.get('Openstack','ADMIN_USER'))
ADMIN_PASS = os.getenv('OS_PASSWORD',parser.get('Openstack','ADMIN_PASS'))
TENANT_NAME= os.getenv('OS_TENANT_NAME',parser.get('Openstack','TENANT_NAME'))
GLANCE_PORT= os.getenv('GLANCE_PORT',parser.get('Openstack','GLANCE_PORT'))
KEYSTONE_ADMIN_PORT=os.getenv('KEYSTONE_ADMIN_PORT',parser.get('Openstack','KEYSTONE_ADMIN_PORT'))

SWIFT_USER=os.getenv('SWIFT_USER',parser.get('Swift','SWIFT_USER'))
SWIFT_KEY= os.getenv('SWIFT_KEY',parser.get('Swift','SWIFT_KEY'))
CONTAINER_NAME=os.getenv('CONTAINER_NAME',parser.get('Swift','CONTAINER_NAME'))
SWIFT_AUTH_URL=os.getenv('SWIFT_AUTH_URL',parser.get('Swift','SWIFT_AUTH_URL'))

auth=os.getenv('PSAR_AUTH_ON',parser.getboolean('Auth','auth'))




def glance_client():
	auth = identity.Password(auth_url='http://' +str(YOUR_IP)+':'+KEYSTONE_ADMIN_PORT+'/v2.0',
                         username=ADMIN_USER,
                         password=ADMIN_PASS,
                         tenant_name=TENANT_NAME)

	sess = session.Session(auth=auth)
	token = auth.get_token(sess)

	return Client('2', endpoint='http://'+YOUR_IP+':'+GLANCE_PORT, token=token)

def swift_conn():
	return swiftclient.Connection(user=SWIFT_USER,key=SWIFT_KEY, authurl=SWIFT_AUTH_URL)

def list_files():
	conn=swift_conn()
	container_name=CONTAINER_NAME
	for data in conn.get_container(container_name)[1]:
        	print '{0}\t{1}\t{2}'.format(data['name'], data['bytes'], data['last_modified'])

def create_image(id=None, namePSA=None):	
	glance=glance_client()
	image = glance.images.create(disk_format='qcow2',container_format='bare')
	if id:
		glance.images.update(image.id,name=id)
		return (id, str(uuid.uuid4()), str(uuid.uuid4()), 
			str(uuid.uuid4()), str(uuid.uuid4()), 
			str(uuid.uuid4()), str(uuid.uuid4()), 
			str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()))

	else:
		glance.images.update(image.id,name=image.id)
		return (image.id, str(uuid.uuid4()), str(uuid.uuid4()), 
			str(uuid.uuid4()), str(uuid.uuid4()), 
			str(uuid.uuid4()), str(uuid.uuid4()), 
			str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()))

	

def upload_file(name,delete=True, ext=None):
	
	conn=swift_conn()
	namestr=str(name)
	container_name=CONTAINER_NAME
	try:
		delete_file(namestr)
	except:
		pass
	with open(namestr,'r') as f:
		conn.put_object(container_name,namestr,contents=f.read(),content_type='text/plain')
	if delete :
		delete_local_file(name)
def download_file(name,ext=None):
	namestr=str(name)
	conn=swift_conn()
	container_name=CONTAINER_NAME
	try:
		obj=conn.get_object(container_name,namestr)
	except:
		raise ObjectDoesNotExist()

	with open(namestr,'w')as f:
		f.write(obj[1])

def delete_file (name,ext=None):
	conn=swift_conn()
	container_name=CONTAINER_NAME
	try:
		conn.delete_object(container_name,str(name))
	except:
		raise ObjectDoesNotExist()

def delete_local_file(name):
	comm = 'rm ' +str(name)
	call(comm,shell=True)
	call('pwd')
def upload_image(name,disk_format,container_format,delete=False, namePSA=None):	
	delete_image(name, namePSA)
	
	namestr=str(name)
	glance = glance_client()		
	#image=glance.images.create(name=namestr)
	image=glance.images.create(name=namestr,container_format=container_format,disk_format=disk_format)
	try:
		glance.images.upload(image.id,open(namestr,'rb'))
	except:
		logging.critical("Error uploading image. Check Glance service")
	#glance.images.upload(open(namestr, 'rb'))
	
	hash_func=hashlib.new('sha256')
	with open(namestr,'rb') as f:
		f.seek(0,os.SEEK_END)
		size=f.tell()
	i=0
	with open(namestr,'rb') as f:
		while i<size:
			hash_func.update(f.read(512))
			i+=512 		
	
	"""
	with open(str(name), 'r') as f:
                call(["glance","--os-username="+ADMIN_USER,"--os_password="+ADMIN_PASS,"--os-tenant-name=admin",
                        "--os-auth-url=http://"+str(YOUR_IP) +":35357/v2.0","image-create","--name",str(name), "--disk-format", disk_format,
                        "--container-format",container_format, "--is-public", "True"], stdin=f)
	"""
	if delete:
		delete_local_file(name)
	
	return hash_func.hexdigest()


def delete_image(name, namePSA=None):
	namestr=str(name)
        glance = glance_client()
	try:
		print getImageIDFromName(glance.images.list(),namestr)
		
		glance.images.delete(getImageIDFromName(glance.images.list(),namestr))
		
	except:
		raise ObjectDoesNotExist()
		


def download_image(name, namePSA=None):

	try:
		namestr=str(name)
		glance=glance_client()
		d = glance.images.data(getImageIDFromName(glance.images.list(),namestr))
		if d.iterable is not None:
			with open(namestr,'w') as f:
				for it in d.iterable:
					f.write(it)
	except:
		logging.critical("Error downloading image. Check Glance service")
def getImageIDFromName(list,name):
        for image in list: 
		if image.name == name:
			return image.id			

	
def check_token(request):
        
	if not auth:
		return True
	
	if 'token' in request.query_params:
                auth_token = request.query_params['token']
                admin_client = client.Client(username=ADMIN_USER, auth_url='http://'+str(YOUR_IP) +':'+KEYSTONE_ADMIN_PORT+'/v2.0', password=ADMIN_PASS)
                try:
                        auth_result = admin_client.tokens.authenticate(token=auth_token)
                        if not auth_result:
                                return False

                        return True
                except:
                       return False
        else:
                return False
	
def upload_psa (name1, name2):
	pass
