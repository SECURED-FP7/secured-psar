from subprocess import call
from keystoneclient.v2_0 import client
from keystoneclient.auth.identity import v2 as identity
from keystoneclient import session
import sys, uuid, paramiko, hashlib, os, logging, json, yaml, argparse, argcomplete, requests, uuid, hashlib
from django.core.exceptions import ObjectDoesNotExist
from ConfigParser import SafeConfigParser
from argcomplete.completers import FilesCompleter
from requests import post



parser = SafeConfigParser()
parser.read('psar.conf')
logging.basicConfig(filename=parser.get('logging','filename'),format='%(asctime)s %(levelname)s:%(message)s', level=parser.get('logging','level'))


ADMIN_USER = os.getenv('OS_USERNAME',parser.get('Openstack','ADMIN_USER'))
ADMIN_PASS = os.getenv('OS_PASSWORD',parser.get('Openstack','ADMIN_PASS'))
KEYSTONE_ADMIN_PORT=os.getenv('KEYSTONE_ADMIN_PORT',parser.get('Openstack','KEYSTONE_ADMIN_PORT'))


YOUR_IP = os.getenv('YOUR_IP', parser.get('General','YOUR_IP'))

auth=os.getenv('PSAR_AUTH_ON',parser.getboolean('Auth','auth'))

tenant=parser.get('mano','tenant')
remotePath=parser.get('mano','pathMano')
remoteIp=parser.get('mano','ipMano')
remoteUser=parser.get('mano','userMano')
remotePass=parser.get('mano','passMano')
remotePort=parser.get('mano','portMano')
remoteVNFrepo=parser.get('mano','vnfrepo')
localpathpsar=parser.get('mano','pathlocalpsar')
pathlocal=parser.get('mano','pathfiles')
repoLocalVnf=parser.get('mano','pathYamlVnf')

remoteHost=remoteUser+'@'+remoteIp+':'





def create_image(namePSA, id=None):	
	if id is not None:
		create_vnf(namePSA)
		return (id, str(uuid.uuid4()), str(uuid.uuid4()), 
			str(uuid.uuid4()), str(uuid.uuid4()), 
			str(uuid.uuid4()), str(uuid.uuid4()), 
			str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()))

	else:
		id=str(uuid.uuid4())
		create_vnf(namePSA)		
		return (id, str(uuid.uuid4()), str(uuid.uuid4()), 
			str(uuid.uuid4()), str(uuid.uuid4()), 
			str(uuid.uuid4()), str(uuid.uuid4()), 
			str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4()))

	

def upload_file(name,delete=True, ext=None):
	namestr=str(name)
	namestr=namestr+str(ext)
	try:
		delete_file(namestr)
	except:
		pass
	g=open(pathlocal+namestr, 'w')
	with open(str(name),'r') as f:
               g.write(f.read())
	g.close()
	#os.system('scp "%s" "%s"' (str(pathlocal+namestr), str(remotehost+remotepath+namestr)))
	if delete :
		delete_local_file(name)
	#
def download_file(name, ext=None):
	namestr=str(name)+ext
	try:
		g=open(pathlocal+namestr, 'r')
		#os.system('scp "%s" "%s"' (str(remotehost+remotepath+namestr,str(pathlocal+namestr))))
	except:
		raise ObjectDoesNotExist()
        with open(str(name),'w')as f:
       	        f.write(g.read())
	try:
		g.close()
	except:
		pass

	#
def delete_file (name,ext=None):
	namestr=str(name)
	try:
		g=open(pathlocal+namestr+ext, 'r')
		os.system('rm '+ (str(pathlocal+name+ext)))
	except:
		raise ObjectDoesNotExist()

def delete_local_file(name):
	comm = 'rm ' +str(name)
	call(comm,shell=True)
	call('pwd')
	#

def upload_image(name,disk_format,container_format,namePSA,delete=False ):
	namestr=str(namePSA)
	nameID=str(name)	
	try:
		delete_image(name=nameID,namePSA=namestr)

	except:
		#print 'no ha borrado la imagen'
		pass

	try:
	        transport =paramiko.Transport((remoteIp, int(22)))
        	transport.connect(username=remoteUser, password=remotePass)
      		sftp = paramiko.SFTPClient.from_transport(transport)
		name1='/home/seguridad/psar/'+nameID
		sftp.put(name1, remotePath+namestr+'.'+disk_format)
        	sftp.close()
		transport.close()
		#print 'Upload done'

	except:
		pass
		#print 'no sube imagen'
	#Delete VNF Openmano
	URLrequest = "http://%s:%s/openmano/%s/vnfs" %(remoteIp, remotePort, tenant)
	requests.delete(URLrequest+'/'+namestr)
	
	create_vnf(namePSA, disk_format)

        hash_func=hashlib.new('sha256')
        with open(nameID,'rb') as f:
                f.seek(0,os.SEEK_END)
                size=f.tell()
        i=0
        with open(nameID,'rb') as f:
                while i<size:
                        hash_func.update(f.read(512))
                        i+=512
	if delete:
		delete_local_file(name)
	
	return hash_func.hexdigest()


def download_image(name, namePSA, nameFormat=False):
	try:
		namestr=str(namePSA)

	        transport =paramiko.Transport((remoteIp, int(22)))
        	transport.connect(username=remoteUser, password=remotePass)
      		sftp = paramiko.SFTPClient.from_transport(transport)
		archivos = sftp.listdir(remotePath)
		for archivo in archivos:
    			g=archivo.split('.')
			if g[0]==namestr:
      				nameformat=g[1]
				print archivo


		import sys
		#namelocal=localpathpsar+nameformat
		namelocal=localpathpsar+name
                if nameFormat:
                        namelocal=localpathpsar+name+'.'+nameformat
		sftp.get(remotePath+name+'.'+nameformat, namelocal)
        	sftp.close()
		transport.close()
		#print 'Download done'


	except:
		logging.critical("Error downloading image.")


def upload_psa(newname, oldname):
	URLrequest = "http://%s:%s/openmano/%s/vnfs" %(remoteIp, remotePort, tenant)
        requests.delete(URLrequest+'/'+oldname)
	delete_image(name=oldname, namePSA=oldname)
	#print 'Delete image done'
        transport =paramiko.Transport((remoteIp, int(22)))
        transport.connect(username=remoteUser, password=remotePass)
        sftp = paramiko.SFTPClient.from_transport(transport)
        archivos = sftp.listdir(remotePath)
	format=None
        for archivo in archivos:
                g=archivo.split('.')
                if g[0]==oldname:
                        nameformat=archivo
			format=g[1]
	create_vnf(name=newname,format=format)


def delete_image(name,namePSA):
	namestr=str(namePSA)
	nameformat=namestr
	transport =paramiko.Transport((remoteIp, int(22)))
	transport.connect(username=remoteUser, password=remotePass)
	sftp = paramiko.SFTPClient.from_transport(transport)
	archivos = sftp.listdir(remotePath)
	for archivo in archivos:
    		g=archivo.split('.')
		if g[0]==namestr:
      			nameformat=archivo

	try:
		sftp.remove(str(remotePath+nameformat))
		sftp.close()
		transport.close()
	except:
		pass
		#print 'No such image'

	try:
	        transport =paramiko.Transport((remoteIp, int(22)))
        	transport.connect(username=remoteUser, password=remotePass)
	        sftp = paramiko.SFTPClient.from_transport(transport)
		sftp.remove(str(remoteVNFrepo+namestr+'.vnfd'))
		sftp.close()
		transport.close()
	except:
		pass
		#print 'No such image'
	try:
		os.system('rm "%s"' %(str(repoLocalVnf+namestr+'.yaml')))
	except:
		pass


	URLrequest = "http://%s:%s/openmano/%s/vnfs" %(remoteIp, remotePort, tenant)
	requests.delete(URLrequest+'/'+namestr)

	#print 'Delete image done'



	
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
	


def getImageIDFromName(list,name):
        for image in list:
                if image.name == name:
                        return image.id






def create_vnf(name, format=None):
	if format is None:
		parseVnf(name)
	else:
		parseVnf(name, format)
	doc=repoLocalVnf+name+'.yaml'
	dataset=yaml.load(open(doc,'rb'))
	headers_req = {'Accept': 'application/json', 'content-type': 'application/json'}
	URLrequest = "http://%s:%s/openmano/%s/vnfs" %(remoteIp, remotePort, tenant)
	mano_response=requests.post(URLrequest, headers = headers_req, data=dataset)
	t = _print_verbose(mano_response)	
	print t
	return 




def parseVnf(nameVNF, format=None):

        nameDoc=nameVNF+'.yaml'
        #pathDoc=parser.get('mano','pathimages')
	pathDoc=repoLocalVnf
        if format is None:
                pathImage='/no/path/image.qcow'
        else:
                pathImage=remotePath+nameVNF+'.'+format



        string1="""'{"vnf":
{"VNFC":
[{"VNFC image": """
        string2=""",
"description": "Dataplane VM",
"bridge-ifaces": [{"vpci": "0000:00:09.0",
"bandwidth": "1 Mbps",
"name": "eth0"},
{"vpci": "0000:00:10.0",
"bandwidth": "1 Mbps",
"name": "eth1"}],
"numas": [{"cores": 3,
"interfaces": [{"vpci": "0000:00:11.0",
"bandwidth": "10 Gbps",
"dedicated": "yes",
"name": "xe0"},
{"vpci": "0000:00:12.0",
"bandwidth": "10 Gbps",
"dedicated": "yes",
"name": "xe1"},
{"vpci": "0000:00:13.0",
"bandwidth": "1 Gbps",
"dedicated": "no",
"name": "xe2"}],
"memory": 8}],
"name": "dataplaneVNF2-VM"}],
"description": "Example of a dataplane VNF",
"external-connections":
[{"local_iface_name": "eth0",
"VNFC": "dataplaneVNF2-VM",
"type": "mgmt",
"name": "mgmt",
"description": "Management interface for general use"},
{"local_iface_name": "eth1",
"VNFC": "dataplaneVNF2-VM",
"type": "bridge",
"name": "control",
"description": "Bridge interface"},
{"local_iface_name": "xe0",
"VNFC": "dataplaneVNF2-VM",
"type": "data",
"name": "xe0",
"description": "Dataplane interface 1"},
{"local_iface_name": "xe1",
"VNFC": "dataplaneVNF2-VM",
"type": "data",
"name": "xe1",
"description": "Dataplane interface 2"},
{"local_iface_name": "xe2",
"VNFC": "dataplaneVNF2-VM",
"type": "data",
"name": "xe2",
"description": "Dataplane interface 3 (SR-IOV)"}],
"name": """
        string3="""}}'"""



        f=open(str(pathDoc+nameDoc), 'w')
        f.write(string1)
        f.write('"'+pathImage+'"')
        f.write(string2)
        f.write('"'+nameVNF+'"')
        f.write(string3)
        f.close()
        return






def _print_verbose(mano_response, verbose_level=0):
    content = mano_response.json()
    result = 0 if mano_response.status_code==200 else mano_response.status_code
    if type(content)!=dict or len(content)!=1:
        #print "Non expected format output"
        print str(content)
        return result

    val=content.values()[0]
    if type(val)==str:
        print val
        return result
    elif type(val) == list:
        content_list = val
    elif type(val)==dict:
        content_list = [val]
    else:
        #print "Non expected dict/list format output"
        print str(content)
        return result

    #print content_list
    if verbose_level==None:
        verbose_level=0
    if verbose_level >= 3:
        print yaml.safe_dump(content, indent=4, default_flow_style=False)
        return result
    id=''
    if mano_response.status_code == 200:
        for content in content_list:
            myoutput = "%s %s" %(content['uuid'].ljust(38),content['name'].ljust(20))
            id= content['uuid'].ljust(38)

            if verbose_level >=1:
                myoutput += " " + content['created_at'].ljust(20)
                if verbose_level >=2:
                    new_line='\n'
                    if 'type' in content and content['type']!=None:
                        myoutput += new_line + "  Type: " + content['type'].ljust(29)
                        new_line=''
                    if 'description' in content and content['description']!=None:
                        myoutput += new_line + "  Description: " + content['description'].ljust(20)
            print myoutput
    else:
        print content['error']['description']
    #return id
    return result


