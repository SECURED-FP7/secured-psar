from requests import get, put, post, delete
from client import Client
import json, hashlib, os
from subprocess import call
import urllib2

PSAR_URL = os.getenv('PSAR_URL','http://195.235.93.146:8080')

IMAGE_PATH='image.img'
MANIFEST_PATH='manifest.xml'
PLUGIN_PATH='plugin.plug'

created_psa_id=None

name = "Test_name"
cost = 2
latency = 2
rating = 2
owner = "Test user"
is_generic = True
psa_description = "Test Description" 

capability_list=['Timing','Filtering_L4']



def test_create_PSA():
	client=Client(PSAR_URL)
	#client=Client(PSAR_URL)
	r=client.create_psa()
		
	assert r.status_code==201
	
	data=json.loads(r.text)
	assert set(('psa_id','psa_name','psa_status','psa_manifest_id','psa_storage_id',
		'plugin_id','psa_image_hash')).issubset(data)
	global created_psa_id
	created_psa_id=data['psa_id']

	r=client.create_psa(id='test_id', cost='Not_number')		
	assert r.status_code==400
	r=client.create_psa(id='test_id', latency='Not_number')		
	assert r.status_code==400
	r=client.create_psa(id='test_id', rating='Not_number')		
	assert r.status_code==400



def test_update_PSA():
	client=Client(PSAR_URL)
	r=client.put_image(psa_id=created_psa_id,name=name,cost=cost,latency=latency,rating=rating,is_generic=is_generic,owner=owner,psa_description=psa_description)
	assert r.status_code==200
	r=client.get_image_list(id=created_psa_id)
	data=json.loads(r.text)

	assert data[0]['psa_name']==name
	assert data[0]['cost']==cost
	assert data[0]['latency']==latency
	assert data[0]['rating']==rating
	assert data[0]['owner']==owner
	assert data[0]['is_generic']==is_generic
	assert data[0]['psa_description']==psa_description


	r=client.put_image(psa_id=created_psa_id, name=name,cost='error',latency=latency,rating=rating,is_generic=is_generic,owner=owner,psa_description=psa_description)
	assert r.status_code==400

	r=client.create_psa(name='test_name1',id='test_id1')
	r=client.put_image(psa_id=created_psa_id, name='test_name1',cost='error',latency=latency,rating=rating,is_generic=is_generic,owner=owner,psa_description=psa_description)
	assert r.status_code==409
	
        r=client.delete_psa('test_id1')


def test_opt_par():
        client=Client(PSAR_URL)
		
	r=client.get_psa_opt_par(psa_id=created_psa_id)
	
	data=json.loads(r.text)

	assert data['cost']==cost
	assert data['latency']==latency
	assert data['rating']==rating



	

def test_upload_image():

        try:
                with open(IMAGE_PATH,'rb'):
                        pass
        except:

                url =  'https://launchpadlibrarian.net/83303699/cirros-0.3.0-i386-disk.img'

                file_name = IMAGE_PATH
                u = urllib2.urlopen(url)
                f = open(file_name, 'wb')
                meta = u.info()
                file_size = int(meta.getheaders("Content-Length")[0])
                print "Downloading: %s Bytes: %s" % (file_name, file_size)

                file_size_dl = 0
                block_sz = 8192
                while True:
                        buffer = u.read(block_sz)
                        if not buffer:
                                break

                        file_size_dl += len(buffer)
                        f.write(buffer)
                        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
                        status = status + chr(8)*(len(status)+1)
                        print status,

                f.close()



	client=Client(PSAR_URL)

	r=client.put_image_file(created_psa_id,IMAGE_PATH,'qcow2','bare')
	assert r.status_code==200
	

	list=client.get_image_list(id=created_psa_id)
	data=json.loads(list.text)[0]

	assert data['psa_image_hash']==calculate_hash(IMAGE_PATH)
	
	

def calculate_hash(path):

	hash_func=hashlib.new('sha256')
        with open(path,'rb') as f:
                f.seek(0,os.SEEK_END)
                size=f.tell()
        i=0
        with open(path,'rb') as f:
                while i<size:
                        hash_func.update(f.read(512))
                        i+=512
	return hash_func.hexdigest()


def test_download_image():
        client=Client(PSAR_URL)
	r=client.get_image_file(created_psa_id,'downloaded_image.img')
	assert r.status_code==200
	
	list=client.get_image_list(id=created_psa_id)
        data=json.loads(list.text)[0]

        #assert data['psa_image_hash']==calculate_hash('downloaded_image.img')

	r=client.get_image_file('NoPSA_ID','downloaded_image.img')
	assert r.status_code==404

	
		
def test_delete_image():
	client=Client(PSAR_URL)
        r=client.delete_image(created_psa_id)
        assert r.status_code==204

        list=client.get_image_list(id=created_psa_id)
        data=json.loads(list.text)[0]

        assert data['psa_image_hash']==''

	r=client.delete_image('Not_id_psa')
	assert r.status_code==404

def test_upload_manifest():

        try:
                with open(MANIFEST_PATH,'rb'):
                        pass
        except:
		with open(MANIFEST_PATH,'wb')as f:
			f.write('Everything Ok')

	client = Client(PSAR_URL)

	r=client.put_manifest_file(created_psa_id,MANIFEST_PATH)
        assert r.status_code==200
	
	r=client.put_manifest_file('Not_id_exist',MANIFEST_PATH)
        assert r.status_code==404

        r=client.get_psa_opt_par(psa_id=created_psa_id)
        data=json.loads(r.text)

        assert data['cost']==8.0
        assert data['latency']==9.0
        assert data['rating']==10.0



def test_capabilities():

	client = Client(PSAR_URL)
	r=client.get_psa_capabilities(psa_id=created_psa_id)
	data=json.loads(r.text)	
	
	for capability in capability_list:	
		assert capability in data['capabilities']


	

def test_download_manifest():
        client = Client(PSAR_URL)
        r=client.get_manifest(created_psa_id,'downloaded_manifest.xml')
        assert r.status_code==200
	with open('downloaded_manifest.xml','rb') as f,open(MANIFEST_PATH,'rb') as f2:
		text=f.read()
		text2=f2.read()
		assert text==text2

def test_delete_manifest():
        client = Client(PSAR_URL)
        r=client.delete_manifest(created_psa_id)
        assert r.status_code==204

        r=client.get_psa_capabilities(psa_id=created_psa_id)
        assert r.status_code==200
        data=json.loads(r.text)
	assert data['capabilities']==[]




def test_upload_plugin():

        try:
                with open(PLUGIN_PATH,'rb'):
                        pass
        except:
                with open(PLUGIN_PATH,'wb')as f:
                        f.write('Everything Ok')



	client = Client(PSAR_URL)
        r=client.put_plugin_file(created_psa_id,PLUGIN_PATH)
        assert r.status_code==200


        r=client.put_plugin_file('Not_id_psa',PLUGIN_PATH)
        assert r.status_code==404




def test_download_plugin():
        client = Client(PSAR_URL)
        r=client.get_plugin_file(created_psa_id,'downloaded_plugin.plug')
        assert r.status_code==200
        with open('downloaded_plugin.plug','rb') as f,open(PLUGIN_PATH,'rb') as f2:
                text=f.read()
                text2=f2.read()
                assert text==text2
        r=client.get_plugin_file('Not_id_psa','downloaded_plugin.plug')
        assert r.status_code==404


def test_delete_plugin():
        client = Client(PSAR_URL)
        r=client.delete_plugin(created_psa_id)
        assert r.status_code==204

        r=client.delete_plugin(created_psa_id)
        assert r.status_code==404
        




	

def test_custom_id_and_name():
		
	test_id= 'TestID'	
	test_name= 'TestName'
	client=Client(PSAR_URL)
	r=client.create_psa(name=test_name,id=test_id)
	with open('err.html','wb') as f:
		f.write(r.text)
	assert r.status_code==201

	r=client.create_psa(name=test_name,id=test_id)
	assert r.status_code==409

	data=json.loads(r.text)
	assert data['psa_name']==test_name
	assert data['psa_id']==test_id
	
	r=client.delete_psa(test_id)
	assert r.status_code==204
	
def test_dyn_conf():
	location='TestLocation'
	dyn_conf='TestDynConf'
	new_dyn_conf='NewTestDynConf'
        global created_psa_id
	client=Client(PSAR_URL)

	r=client.put_dyn_conf(psa_id=created_psa_id, location=location, dyn_conf=dyn_conf)
	assert r.status_code==201

	r=client.put_dyn_conf(psa_id=created_psa_id, location=location, dyn_conf=new_dyn_conf)
	assert r.status_code==200

	r=client.get_dyn_conf(psa_id=created_psa_id, location=location)
	data=json.loads(r.text)
	assert data['dyn_conf']==new_dyn_conf

	r=client.delete_dyn_conf(psa_id=created_psa_id, location=location)
	assert r.status_code==204

	r=client.get_dyn_conf(psa_id=created_psa_id, location=location)
	assert r.status_code==404
	

def test_delete_PSA():

        client=Client(PSAR_URL)
        global created_psa_id
        r=client.delete_psa(created_psa_id)
        created_psa_id=''
        assert r.status_code==204



