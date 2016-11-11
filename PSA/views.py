from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from models import PSA,  PSA_manifest, PSAR_local, PSA_storage, M2L_Plugin, PSACapabilityAssociation, Capability, dynamic_Conf
from serializers import PSAOptimizationParameterSerializer, PSASerializer, PSASerializerMini, PSAManifestSerializer, PSACapabilityAssociationSerializer, dynamic_ConfSerializer
from subprocess import call
from django.core.exceptions import ObjectDoesNotExist
from PSA_status import *
from ConfigParser import SafeConfigParser
from wsgiref.util import FileWrapper
from django.http import HttpResponse
from django.db.models import Q
import os, logging
import xml.etree.ElementTree as ET
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse
from rest_framework.parsers import FileUploadParser, MultiPartParser
from subprocess import call
from xml.dom import minidom


parser = SafeConfigParser()
parser.read('psar.conf')
logging.basicConfig(filename=parser.get('logging','filename'),format='%(asctime)s %(levelname)s:%(message)s', level=parser.get('logging','level'))

repository=parser.get('repository','repository')

if repository=='OPENMANO':
	from scriptsOpenmano import upload_file, download_file, delete_file, download_image, upload_image, delete_image, delete_local_file, check_token, create_image, upload_psa
else:
	from scripts import upload_file, download_file, delete_file, download_image, upload_image, delete_image, delete_local_file, check_token, create_image, upload_psa


class PSAList(APIView):
	"""
	"""
	
	def get(self, request):
		"""
		Shows a list of all existing PSAs. Accepts paramater 'id'(AMONG OTHERS, STILL DEFINING) and, if it exists, shows only  matching PSAs

		Returns PSAs according to the query

                token -- (NOT required)
                id -- (NOT required)
                cost -- (NOT required)
                latency -- (NOT required)
		rating -- (NOT required)
                owner -- (NOT required)
		is_generic -- (NOT required)
                capability -- (NOT required)

                """
                if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/PSA/images/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)
                objects = PSA.objects.all()
                if 'capability' in request.query_params:
                        psas=PSACapabilityAssociation.objects.filter(capability=request.query_params['capability'])
                        if len(psas)==0:
                                return Response(data={})
                        query=Q()
                        for psa in psas:
                                query=query | Q(psa_id=psa.psa.psa_id)
                        objects=objects.filter(query)


                if 'id' in request.query_params:
                        objects = objects.filter(psa_id=str(request.query_params['id']))
                if 'is_generic' in request.query_params:
			b = request.query_params['is_generic'].lower()
			if b == 'false' or b == 'true':
	                        objects = objects.filter(is_generic= parseBoolString(request.query_params['is_generic']))
			else:
                               logging.warning('%s %s: 400 BAD REQUEST',request.method,'/v1/PSA/images/')
                               return Response(status=status.HTTP_400_BAD_REQUEST)
                if 'cost' in request.query_params:
                        cost=request.query_params['cost']
                        try:
                                float(cost)
                        except:
                               logging.warning('%s %s: 400 BAD REQUEST',request.method,'/v1/PSA/images/')
                               return Response(status=status.HTTP_400_BAD_REQUEST)

                        objects = objects.filter(cost=request.query_params['cost'])
                if 'latency' in request.query_params:
                        latency=request.query_params['latency']
                        try:
                                float(latency)
                        except:
                               logging.warning('%s %s: 400 BAD REQUEST',request.method,'/v1/PSA/images/')
                               return Response(status=status.HTTP_400_BAD_REQUEST)
                        objects = objects.filter(latency=request.query_params['latency'])
                if 'rating' in request.query_params:
                        rating=request.query_params['rating']
                        try:
                                float(rating)
                        except:
                               logging.warning('%s %s: 400 BAD REQUEST',request.method,'/v1/PSA/images/')
                               return Response(status=status.HTTP_400_BAD_REQUEST)
                        objects = objects.filter(rating=request.query_params['rating'])

                if 'owner' in request.query_params:
                        objects = objects.filter(owner=request.query_params['owner'])



		#Add other parameters to filer
		serial = PSASerializer(objects,many=True)
		#return Response(status=status.HTTP_200_OK)
                logging.info('%s %s: 200 OK',request.method,'/v1/PSA/images/')
		return Response(data=serial.data)
	
	def post(self,request):
		"""
		Create a new (empty)PSA and associated tables. Returns JSON with data of the PSA
		
		---
                    parameters:
                    - name: token
      		      description: (NOT required)
                      required: false
                      type: string
		    - name: name
		      description: (NOT required)
                      required: false
                      type: string
		    - name: id
		      description: (NOT required)
                      required: false
                      type: string
		    - name: plugin_id
		      description: (NOT required)
                      required: false
                      type: string
		    - name: manifest_id
		      description: (NOT required)
                      required: false
                      type: string
		    - name: psa_storage_id
		      description: (NOT required)
                      required: false
                      type: string
		    - name: general_info_id 
		      description: (NOT required)
                      required: false
                      type: string
		    - name: funcionality_id 
		      description: (NOT required)
                      required: false
                      type: string
		    - name: execution_model_id 
		      description: (NOT required)
                      required: false
                      type: string
		    - name: configuration_model_id
		      description: (NOT required)
                      required: false
                      type: string
		    - name: monitoring_id
		      description: (NOT required)
                      required: false
                      type: string
		    - name: custom_id
		      description: (NOT required)
                      required: false
                      type: string
		    - name: psa_description
		      description: (NOT required)
                      required: false
                      type: string
		    - name: is_generic
		      description: (NOT required)
                      required: false
                      type: boolean
		    - name: owner
		      description: (NOT required)
                      required: false
                      type: string
		    - name: cost
		      description: (NOT required)
                      required: false
                      type: float
		    - name: latency
		      description: (NOT required)
                      required: false
                      type: float
		    - name: rating
		      description: (NOT required)
                      required: false
                      type: float
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/PSA/images/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		psa = PSA(psa_id='psa_id', psa_name='name',
       	        	psa_status='0', psa_manifest_id='manifest_id',
       	       		psa_storage_id = 'psa_storage_id',plugin_id = 'plugin_id', 
			cost='0', latency='0', rating='0', is_generic='is_generic',
			owner='owner', psa_description='psa_description')

		psa.save()
		id=psa.id

		psa.delete()
		name='PSA_'+str(id)
                if 'name' in request.data:
			try:
        	                psa = PSA.objects.get(psa_name=request.data['name'])
                	        logging.info('%s %s: 409 CONFLICT',request.method,'/v1/PSA/images/')
                        	return Response(status=status.HTTP_409_CONFLICT,data=PSASerializer(psa).data)
			except ObjectDoesNotExist:
				pass

			name=request.data['name']
		logging.info("Creating PSA")
		ids = None
		if 'id' in request.data:
			try:
        	                psa = PSA.objects.get(psa_id=request.data['id'])
                	        logging.info('%s %s: 409 CONFLICT',request.method,'/v1/PSA/images/')
                        	return Response(status=status.HTTP_409_CONFLICT,data=PSASerializer(psa).data)
	
        	        except ObjectDoesNotExist:
				pass

			ids = create_image(id=request.data['id'], namePSA=name)
		else:
			ids=create_image(namePSA=name)
		psa_id=ids[0]
		if 'plugin_id' in request.data:
			try:
        	                psa = PSA.objects.get(plugin_id=request.data['plugin_id'])
                	        logging.info('%s %s: 409 CONFLICT',request.method,'/v1/PSA/images/')
                        	return Response(status=status.HTTP_409_CONFLICT,data=PSASerializer(psa).data)
			except ObjectDoesNotExist:
				pass

			plugin_id=request.data['plugin_id']
		else:
			plugin_id=ids[1]
	
		if 'manifest_id' in request.data:
			try:
        	                psa = PSA.objects.get(psa_manifest_id=request.data['manifest_id'])
                	        logging.info('%s %s: 409 CONFLICT',request.method,'/v1/PSA/images/')
                        	return Response(status=status.HTTP_409_CONFLICT,data=PSASerializer(psa).data)
			except ObjectDoesNotExist:
				pass

			manifest_id=request.data['manifest_id']
		else:
			manifest_id=ids[2]
	
		if 'psa_storage_id' in request.data:
			psa_storage_id=request.data['psa_storage_id']
		else:
			psa_storage_id=ids[3]

		if 'general_info_id' in request.data:
			general_info_id=request.data['general_info_id']
		else:
			general_info_id=ids[4]

		if 'funcionality_id' in request.data:
			funcionality_id=request.data['funcionality_id']
		else:
			funcionality_id=ids[5]

		if 'execution_model_id' in request.data:
			execution_model_id=request.data['execution_model_id']
		else:
			execution_model_id=ids[6]

		if 'configuration_id' in request.data:
			configuration_id=request.data['configuration_id']
		else:
			configuration_id=ids[7]

		if 'monitoring_id' in request.data:
			monitoring_id=request.data['monitoring_id']
		else:
			monitoring_id=ids[8]

		if 'custom_id' in request.data:
			custom_id=request.data['custom_id']
		else:
			custom_id=ids[9]

                if 'cost' in request.data:
                        cost=request.data['cost']
			try:
				float(cost)
			except:
                               logging.warning('%s %s: 400 BAD REQUEST',request.method,'/v1/PSA/images/'+psa_id)
                               return Response(status=status.HTTP_400_BAD_REQUEST)
		else: 
			cost=0.0

                if 'latency' in request.data:
                        latency=request.data['latency']
			try:
				float(latency)
			except:
                               logging.warning('%s %s: 400 BAD REQUEST',request.method,'/v1/PSA/images/'+psa_id)
                               return Response(status=status.HTTP_400_BAD_REQUEST)
		else:
			latency=0.0

                if 'rating' in request.data:
                       	rating=request.data['rating']
			try:
				float(rating)
			except:
                               logging.warning('%s %s: 400 BAD REQUEST',request.method,'/v1/PSA/images/'+psa_id)
                               return Response(status=status.HTTP_400_BAD_REQUEST)
		else:
			rating=0.0
                if 'is_generic' in request.data:

                        is_generic=request.data['is_generic']
                else:
                        is_generic=False
                if 'owner' in request.data:
                        owner=request.data['owner']
                else:
                        owner=''
                if 'psa_description' in request.data:
                        psa_description=request.data['psa_description']
                else:
                        psa_description=''



		
		"""
                psa_id, plugin_id, manifest_id, psa_storage_id, 
		general_info_id, funcionality_id, execution_model_id, 
		configuration_id, monitoring_id, custom_id=create_image(), cost, latency, rating, is_generic, owner, psa_description
      	        """
		psa = PSA(id=id,psa_id=psa_id, psa_name=name,
       	        	psa_status='0', psa_manifest_id=manifest_id,
       	       		psa_storage_id = psa_storage_id,plugin_id = plugin_id, 
			cost=cost, latency=latency, rating=rating, is_generic=is_generic,
			owner=owner, psa_description=psa_description)
		
     	       	psa.save()

		manifest = PSA_manifest(psa_manifest_id=manifest_id,
			name=name,general_info_id =general_info_id, 
			funcionality_id = funcionality_id, execution_model_id=execution_model_id,
			configuration_id=configuration_id,monitoring_id=monitoring_id,
			custom_id=custom_id)
		manifest.save()

		plugin = M2L_Plugin(plugin_id=plugin_id)
		plugin.save()


			
		serial = PSASerializer(psa)
                logging.info('%s %s: 200 OK',request.method,'/v1/PSA/images/')
                logging.debug('Request params: %s',request.query_params)
                logging.debug('Response data: %s',serial.data)
        	return Response(status=status.HTTP_201_CREATED,data=serial.data)
		
		
		
def get_manifest (psa_id):
	try:
		psa = PSA.objects.get(psa_id=psa_id)
		man_id = psa.psa_manifest_id
		man = PSA_manifest.objects.get(psa_manifest_id=man_id)
		return man
	except ObjectDoesNotExist:
		return None
class PSAManifestView(APIView):
	"""
	Interacts with the Manifest Storage
	"""

	def get(self, request, psa_id):
		"""
		Downloads the Manifest of the PSA identified by psa_id. 
		token -- (NOT required)
		"""
                if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/PSA/manifest/'+psa_id+'/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		try:
			
			"""
			man = get_manifest(psa_id)
			#return Response(PSAManifestSerializer(man).data)
			download_file(man.psa_manifest_id, ext='.xml')
			#xml=open(man.name).read()
			with open (man.psa_manifest_id, "r") as myfile:
				xml=myfile.read().replace("\n", "")
			delete_local_file(man.psa_manifest_id)
			return Response (xml)
			"""

                        psa=PSA.objects.get(psa_id=psa_id)
			logging.info("Downloading Manifest of PSA %s from storage",psa_id)

                        download_file(psa.psa_manifest_id, ext='.xml')
                        #print call('ls')
                        #plugin=M2L_Plugin.objects.get(plugin_id=psa.plugin_id)
                        filename = str(psa.psa_manifest_id)
			logging.info("Sending Manifest")
                        wrapper = FileWrapper(file(filename))
                        response = HttpResponse(wrapper, content_type='text/plain', status=status.HTTP_200_OK)
                        response['Content-Length'] = os.path.getsize(filename)
                        delete_local_file(filename)
	                logging.info('%s %s: 200 OK',request.method,'/v1/PSA/manifest/'+psa_id+'/')
                        return response

		except ObjectDoesNotExist:
	                logging.warning('%s %s: 404 NOT FOUND',request.method,'/v1/PSA/manifest/'+psa_id+'/')
			return Response (status=status.HTTP_404_NOT_FOUND)

	def put(self,request,psa_id):
		"""
		Updates the information about the manifest on the DB. In the current model, there are no field which can be updated
		token -- (NOT required)
		"""
                if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/PSA/manifest/'+psa_id+'/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		pass

class PSACapabilitiesView(APIView):
	"""
	"""
	def get(self,request,psa_id):
                """
		Get capabilities parsed from manifest
		Example:
	
		GET PSAR_URL/v1/PSA/capabilities/12345/
	
		Return:
			{
  				"capabilities": [
        				"Timing",
        				"Filtering_L4"
	    			]
			}


                token -- (NOT required)
                """

                if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/PSA/capabilities/'+psa_id+'/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		try:
			psa=PSA.objects.get(psa_id=psa_id)
			capabilities=PSACapabilityAssociation.objects.filter(psa=psa_id)
			ser=PSACapabilityAssociationSerializer(capabilities,many=True)

			data={}
			cap=[]
			for c in ser.data:
				cap=cap+[c['capability']]
			data['capabilities']=cap

	                logging.info('%s %s: 200 OK',request.method,'/v1/PSA/capabilities/'+psa_id+'/')

			return Response (status=status.HTTP_200_OK,data=data)

		except ObjectDoesNotExist:
	                logging.warning('%s %s: 404 NOT FOUND',request.method,'/v1/PSA/capabilities/'+psa_id+'/')
			return Response (status=status.HTTP_404_NOT_FOUND)
			
class PSAManifestFileView(APIView):
	def put(self, request, psa_id):
		"""
		Uploads a new Manifest for the PSA identified by psa_id
		token -- (NOT required)
		"""
                if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/PSA/manifest/'+psa_id+'/file')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)
		try:
			#man=PSA_manifest.objects.get(psa_manifest_id=PSA.objects.get(psa_id=psa_id).psa_manifest_id)
			man=PSA.objects.get(psa_id=psa_id).psa_manifest_id
		except ObjectDoesNotExist:
	                logging.warning('%s %s: 404 NOT FOUND',request.method,'/v1/PSA/manifest/'+psa_id+'/file')
			return Response (status=status.HTTP_404_NOT_FOUND)
		#except:
		#	print "Exception"	
		#handle_uploaded_file(request.FILES['manifest'],man.psa_manifest_id)
		logging.info("Receiving Manifest for PSA %s",psa_id)
		with open(man,'wb+')as f:
			for chunk in request.data['file'].chunks():
				f.write(chunk)

		#borra las capabilitis asociadas a esa psa_id
                capabilities=PSACapabilityAssociation.objects.filter(psa=psa_id)
                for c in capabilities:
                        c.delete()

		"""		
		parse XML and add capabilities
		"""
		dom=minidom.parse(man)
               	logging.info('Trying to extract capabilities from Manifest')
		elements = dom.getElementsByTagName('capability_list')
		print elements
		for c in elements:	
			capability=getText(c.childNodes)

			PSAcapability=PSACapabilityAssociation(psa=psa_id, capability=capability)
			PSAcapability.save()
			logging.debug('New capability: %s', capability)
                psa=PSA.objects.get(psa_id=psa_id)
                psa_description1=''
                try:
                        des=dom.getElementsByTagName('description')[0]
                        description=getNodeText(des)
                        psa.psa_description=description
                        psa.save()
                except:
                        logging.info("The manifest don't have description")
                try:
                        opt_param_list=dom.getElementsByTagName('optimization_parameter')
                        opt_param=opt_param_list[0]
                        try:
                                cost=opt_param.attributes["cost"]
                                cost_val=cost.value
                                psa.cost=cost_val
                        except:
                                pass
                        try:
                                latency=opt_param.attributes["latency"]
                                latency_val=latency.value
                                psa.latency=latency_val
                        except:
                                pass
                        try:
                                rating=opt_param.attributes["rating"]
                                rating_val=rating.value
                                psa.rating=rating_val
                        except:
                                pass
                        psa.save()
                except:
                        logging.info("The manifest don't have optimization parameters")

		logging.info("Uploading Manifest to storage")
		upload_file(name=man, ext='.xml')
		
                logging.info('%s %s: 200 OK',request.method,'/v1/PSA/manifest/'+psa_id+'/file')
		return Response(status=status.HTTP_200_OK)		
	
	def delete(self,request, psa_id):
		"""
		Deletes the Manifest asociated with the PSA identified by psa_id
		token -- (NOT required)
		"""
                if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/PSA/manifest/'+psa_id+'/file')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)


		
		try:
	                psa=PSA.objects.get(psa_id=psa_id)
			delete_file(psa.psa_manifest_id,ext='.xml')
			logging.info("Deleting Manifest of PSA %s",psa_id)
	                logging.info('%s %s: 204 NO CONTENT',request.method,'/v1/PSA/manifest/'+psa_id+'/file')
	                #borra las capabilitis asociadas a esa psa_id
        	        capabilities=PSACapabilityAssociation.objects.filter(psa=psa_id)
                	for c in capabilities:
                        	c.delete()
			return Response(status=status.HTTP_204_NO_CONTENT)

		except:
	                logging.warning('%s %s: 404 NOT FOUND',request.method,'/v1/PSA/manifest/'+psa_id+'/file')
			return Response (status=status.HTTP_404_NOT_FOUND)

def getNodeText(node):
    nodelist = node.childNodes
    result = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            result.append(node.data)
    return ''.join(result)


def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return ''.join(rc)

def handle_uploaded_file(f,name):
	with open (str(name), 'wb+') as temp:
		for chunk in f.chunks():
			temp.write(chunk)
	call("awk '{if (NR>3) {print}}' "+name+"  > "+name+"_tmp",shell=True)
	call("sed '$d' "+name+"_tmp > "+name,shell=True) 
	delete_local_file(name+"_tmp")

class PSAFileView(APIView):
	"""
	"""
	parser_classes = (FileUploadParser,)

	def get(self,request,psa_id):
		"""
		Downloads the image file of the PSA identified by psa_id
		

		token -- (NOT required)

		"""		
                if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/PSA/images/'+psa_id+'/file')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		try:
			
			psa=PSA.objects.get(psa_id=psa_id)
			logging.info("Downloading Image of PSA %s from storage",psa_id)
			download_image(psa.psa_id, psa.psa_name)
			filename = str(psa.psa_id)								
			import os.path 
			if os.path.exists(filename): 
				wrapper = FileWrapper(file(filename))
				logging.info("Sending File. This may take a while.")
				response = HttpResponse(wrapper, content_type='text/plain', status=status.HTTP_200_OK)
				response['Content-Length'] = os.path.getsize(filename)
				delete_local_file(filename)
	                	logging.info('%s %s: 200 OK',request.method,'/v1/PSA/images/'+psa_id+'/file')
				return response
			else:
		                logging.warning('%s %s: 404 NOT FOUND',request.method,'/v1/PSA/images/'+psa_id+'/file')
				return Response(status=status.HTTP_404_NOT_FOUND)
				
		except ObjectDoesNotExist:
	                logging.warning('%s %s: 404 NOT FOUND',request.method,'/v1/PSA/images/'+psa_id+'/file')
			return Response(status=status.HTTP_404_NOT_FOUND)
		
	def put (self,request,psa_id):
		"""
                Uploads a new image for the PSA identified by psa_id. The new image must be under the parameter 'image'
                If a PSA identified by psa_id does not exist, creates one.In this case it will be necessary to include a set of parameters ('id', 'name', 'id', 'plugin_id', 'manifest_id', 'psa_storage_id', 'general_info_id', 'funcionality_id', 'execution_model_id', 'configuration_model_id', 'monitoring_id', 'custom_id', 'psa_description', 'is_generic', 'owner', 'cost', 'latency', 'rating') 
                In any case, it must include both parameters 'disk_format' ( qcow2, raw, vhd, vmdk, vdi, iso, aki, ari or ami) and 'container_format' (bare, ovf, aki, ari, ami)
		token -- (NOT required)
		disk_format -- (required)
		container_format -- (required)

                """

                if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/PSA/images/'+psa_id+'/file')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

                psa = None
		
		try:
			psa=PSA.objects.get(psa_id=psa_id)
		except ObjectDoesNotExist:
	                logging.warning('%s %s: 404 NOT FOUND',request.method,'/v1/PSA/images/'+psa_id+'/file')
			return Response(status=status.HTTP_404_NOT_FOUND)	
		else:
			if set(('disk_format','container_format')).issubset(request.query_params):
				print request.data
				#handle_uploaded_file(request.data,psa.psa_id)
				#handle_uploaded_file(request.FILES['file'],psa.psa_id)
				#handle_uploaded_file(request.data['file'],psa.psa_id)
				
				
				logging.info("Receiving Image for PSA %s . This may take a while",psa_id)
	
				with open(psa.psa_id,'wb')as f:
					for chunk in request.data['file'].chunks():
						 f.write(chunk)
				#call("awk '{if (NR>3) {print}}' "+psa.psa_id+"  > "+psa.psa_id+"_tmp",shell=True)
        			#call("sed '$d' "+psa.psa_id+"_tmp > "+psa.psa_id,shell=True)
        			#delete_local_file(psa.psa_id+"_tmp")
				logging.info("Uploading image to storage. This may take a while")
				psa.psa_image_hash=upload_image(name=psa.psa_id,disk_format=request.query_params['disk_format'],container_format=request.query_params['container_format'], namePSA=psa.psa_name)
				psa.save()
		                logging.info('%s %s: 200 OK',request.method,'/v1/PSA/images/'+psa_id+'/file')
				return Response(status=status.HTTP_200_OK)
			else:
		                logging.warning('%s %s: 400 BAD REQUEST',request.method,'/v1/PSA/images/'+psa_id+'/file')
				return Response(status=status.HTTP_400_BAD_REQUEST)

        def delete(self, request, psa_id):
                """
                Deletes the image of the PSA identified by psa_id
		token -- (NOT required)
                """
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/PSA/images/'+psa_id+'/file')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)
                try:
                        psa = PSA.objects.get(psa_id=psa_id)
			logging.info("Deleting image for PSA %s",psa_id)
                        delete_image(psa.psa_id, psa.psa_name)
                        psa.psa_image_hash=''
			psa.save()
	                logging.info('%s %s: 204 NO CONTENT',request.method,'/v1/PSA/images/'+psa_id+'/file')
			return Response (status=status.HTTP_204_NO_CONTENT)
                except ObjectDoesNotExist:
	                logging.warning('%s %s: 404 NOT FOUND',request.method,'/v1/PSA/images/'+psa_id+'/file')
                        return Response(status=status.HTTP_404_NOT_FOUND)


class PSAView(APIView):
	"""
	Interacts with the PSA images 		
	"""
	def put(self, request, psa_id):
		"""
		Updates the information on the DB about the PSA identified by psa_id (e.g. name)
		token -- (NOT required)
		name -- (NOT required)
		cost -- (NOT required)
		latency -- (NOT required)
		rating -- (NOT required)
		is_generic -- (NOT required)
		owner -- (NOT required)
		psa_description -- (NOT required)
		"""
                if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/PSA/images/'+psa_id+'/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)
		
		try:
			psa = PSA.objects.get(psa_id=psa_id)
			nameOld= psa.psa_name
			print nameOld
			try:
				if 'name' in request.query_params:
					try:
        			                psa1 = PSA.objects.get(psa_name=request.query_params['name'])
						if psa==psa1:
							pass
						else:
                		       			logging.info('%s %s: 409 CONFLICT',request.method,'/v1/PSA/images/'+psa_id+'/')
		        	               		return Response(status=status.HTTP_409_CONFLICT,data=PSASerializer(psa).data)
					except ObjectDoesNotExist:
						pass
					psa.psa_name = request.query_params['name']
					newname= psa.psa_name
					try:
						upload_psa(newname=newname, oldname=nameOld)
					except:
						pass
	        	        if 'cost' in request.query_params:
			                cost=request.query_params['cost']
                		        try:
                        	       		float(cost)
		                	except:
        	        		       	logging.warning('%s %s: 400 BAD REQUEST',request.method,'/v1/PSA/images/')
                	               		return Response(status=status.HTTP_400_BAD_REQUEST)
               	        	        psa.cost = request.query_params['cost']
		                if 'latency' in request.query_params:
		                        latency=request.query_params['latency']
	        	                try:
               			                float(latency)
	                        	except:
        	       		               	logging.warning('%s %s: 400 BAD REQUEST',request.method,'/v1/PSA/images/')
                	       			return Response(status=status.HTTP_400_BAD_REQUEST)
        	        	        psa.latency = request.query_params['latency']
	
        	                if 'rating' in request.query_params:
	        	                rating=request.query_params['rating']
               			        try:
	                               		float(rating)
		                        except:
               			               	logging.warning('%s %s: 400 BAD REQUEST',request.method,'/v1/PSA/images/'+psa_id)
	                        	       	return Response(status=status.HTTP_400_BAD_REQUEST)
	       	                       	psa.rating = request.query_params['rating']
        	               	if 'is_generic' in request.query_params:
                	       		b = request.query_params['is_generic'].lower()
                       			if b == 'false' or b == 'true':
						psa.is_generic =  parseBoolString( request.query_params['is_generic'])
        	       			else:
               			        	logging.warning('%s %s: 400 BAD REQUEST',request.method,'/v1/PSA/images/')
	                        	       	return Response(status=status.HTTP_400_BAD_REQUEST)
				if 'owner' in request.query_params:
        	               	       	psa.owner = request.query_params['owner']
		                if 'psa_description' in request.query_params:
        		                psa.psa_description = request.query_params['psa_description']
	
				psa.save()
				logging.info('%s %s: 200 OK',request.method,'/v1/PSA/images/'+psa_id+'/')
	
        	       	        return Response(status=status.HTTP_200_OK)
			
			except:
        	                logging.warning('%s %s: 400 NOT FOUND',request.method,'/v1/PSA/images/'+psa_id+'/')
	                        return Response(status=status.HTTP_400_BAD_REQUEST)

		except ObjectDoesNotExist:
	                logging.warning('%s %s: 404 NOT FOUND',request.method,'/v1/PSA/images/'+psa_id+'/')
                        return Response(status=status.HTTP_404_NOT_FOUND)



	def patch(self, request, psa_id):
		"""
		Updates the status of the PSA identified by psa_id. The new status is specified with the param 'status'
		token -- (NOT required)
		status -- (required)
		"""


                if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/PSA/images/'+psa_id+'/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		try:
			psa = PSA.objects.get(psa_id=psa_id)
			if 'status' in request.query_params:
				psa.psa_status=request.query_params['status']
				psa.save()
		                logging.info('%s %s: 200 OK',request.method,'/v1/PSA/images/'+psa_id+'/')
				return Response(status=status.HTTP_200_OK)
			else:
		                logging.warning('%s %s: 400 BAD REQUEST',request.method,'/v1/PSA/images/'+psa_id+'/')
				return Response(status=status.HTTP_400_BAD_REQUEST)

		except ObjectDoesNotExist:
	                logging.warning('%s %s: 404 NOT FOUND',request.method,'/v1/PSA/images/'+psa_id+'/')
			return Response(status=status.HTTP_404_NOT_FOUND)
	
	def delete(self, request, psa_id):
		"""
		Deletes the PSA identified by psa_id (all files and DB entries)
		token -- (NOT required)
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/PSA/images/'+psa_id+'/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)
		try:
			logging.info("Deleting PSA with id %s",psa_id)

			psa = PSA.objects.get(psa_id=psa_id)
			try:
				logging.info("-------Deleting Image")
				delete_image(psa.psa_id, psa.psa_name)
			except ObjectDoesNotExist:
				pass 
			try:
				logging.info("-------Deleting Manifest")
				delete_file(psa.psa_manifest_id, ext='.xml')
			except ObjectDoesNotExist:
				pass
			try:
				logging.info("-------Deleting Plugin")
				delete_file(psa.plugin_id, ext='.plug')
			except ObjectDoesNotExist:
                                pass

			plugin = M2L_Plugin.objects.get(plugin_id=psa.plugin_id)

			manifest=PSA_manifest.objects.get(psa_manifest_id=psa.psa_manifest_id)

			psa.delete()
			plugin.delete()
			manifest.delete()
	                logging.info('%s %s: 204 NO CONTENT',request.method,'/v1/PSA/images/'+psa_id+'/')
			return Response (status=status.HTTP_204_NO_CONTENT)
		except ObjectDoesNotExist:
	                logging.warning('%s %s: 404 NOT FOUND',request.method,'/v1/PSA/images/'+psa_id+'/')
			return Response(status=status.HTTP_404_NOT_FOUND)


class PSAOptimizationParameter(APIView):
        def get(self, request, psa_id):

        	"""
        	Get optimization parameter
        	Example:

        	GET PSAR_URL/v1/PSA/opt_par/12345/

       	 	Return:
        	        {
	                        "cost": 4,
                	        "latency" : 0.2,
        	                "rating" :1
	                }
        	token -- (NOT required)
	        """


                if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/PSA/opt_par/'+psa_id+'/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)
                try:
                        psa = PSA.objects.get(psa_id=psa_id)
                	#Add other parameters to filer
                	serial = PSAOptimizationParameterSerializer(psa)
            	        #return Response(status=status.HTTP_200_OK)
        	        logging.info('%s %s: 200 OK',request.method,'/v1/PSA/opt_par/'+psa_id+'/')
                        return Response (status=status.HTTP_200_OK,data=serial.data)

		except ObjectDoesNotExist:
                        logging.warning('%s %s: 404 NOT FOUND',request.method,'/v1/PSA/opt_par/'+psa_id+'/')
                        return Response (status=status.HTTP_404_NOT_FOUND)


class M2LFileView(APIView):
	"""
	Interacts with the M2L plugin storage	
	"""
	def put(self, request, psa_id):
		"""
		Uploads a new plugin for the PSA with id=psa_id. 
		token -- (NOT required)
		"""
                if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/M2Lplugins/'+psa_id+'/file')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)
                try:
                        #man=PSA_manifest.objects.get(psa_manifest_id=PSA.objects.get(psa_id=psa_id).psa_manifest_id)
                        plug=PSA.objects.get(psa_id=psa_id).plugin_id

                except ObjectDoesNotExist:
	                logging.warning('%s %s: 404 NOT FOUND',request.method,'/v1/M2Lplugins/'+psa_id+'/file')
                        return Response (status=status.HTTP_404_NOT_FOUND)
                #except:
                #        print "Exception"
                #handle_uploaded_file(request.FILES['manifest'],man.psa_manifest_id)
                logging.info("Receiving MSLPlugin for PSA %s",psa_id)
		with open(plug,'wb+')as f:
                        for chunk in request.data['file'].chunks():
                                f.write(chunk)
		logging.info("Uploading plugin to storage")
		upload_file(name=plug, ext='.plug')
                logging.info('%s %s: 200 OK',request.method,'/v1/M2Lplugins/'+psa_id+'/file')
               	return Response(status=status.HTTP_200_OK)



	def delete(self, request, psa_id):
		"""
		Deletes the M2LPlugin of the PSA with id=psa_id
		token -- (NOT required)
		"""

                if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/M2Lplugins/'+psa_id+'/file')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		try:
			psa = PSA.objects.get(psa_id=psa_id)
			plug=PSA.objects.get(psa_id=psa_id).plugin_id
			logging.info("Deleting M2LPlugin of PSA %s",psa_id)
			delete_file(psa.plugin_id,ext='.plug')
	                logging.info('%s %s: 204 NO CONTENT',request.method,'/v1/M2Lplugins/'+psa_id+'/file')
			return Response (status=status.HTTP_204_NO_CONTENT)
		except ObjectDoesNotExist:
	                logging.warning('%s %s: 404 NOT FOUND',request.method,'/v1/M2Lplugins/'+psa_id+'/file')
			return Response(status=status.HTTP_404_NOT_FOUND)
	
class M2LView(APIView):
        """
        Interacts with the M2L plugin storage
        """

	def get(self, request, psa_id):
		"""
		Downloads the M2L Plugin of the PSA with id=psa_id
		token -- (NOT required)
		"""

                if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/M2Lplugins/'+psa_id+'/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		try:
			psa=PSA.objects.get(psa_id=psa_id)
			logging.info("Downloading M2LPlugin of PSA %s from storage",psa_id)
			download_file(psa.plugin_id, ext='.plug')
			#print call('ls')
			#plugin=M2L_Plugin.objects.get(plugin_id=psa.plugin_id)
			filename = str(psa.plugin_id)
			logging.info("Sending M2LPlugin")
			wrapper = FileWrapper(file(filename))
			response = HttpResponse(wrapper, content_type='text/plain', status=status.HTTP_200_OK)
			response['Content-Length'] = os.path.getsize(filename)
			delete_local_file(filename)
	                logging.info('%s %s: 200 OK',request.method,'/v1/M2Lplugins/'+psa_id+'/')
			return response
		except ObjectDoesNotExist:
	                logging.warning('%s %s: 404 NOT FOUND',request.method,'/v1/M2Lplugins/'+psa_id+'/')
			return Response(status=status.HTTP_404_NOT_FOUND)
	def put(self, request, psa_id):
		"""
		Updates the information on the database
		token -- (NOT required)
		name -- (NOT required)
		url -- (NOT required)
		"""
		if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/M2Lplugins/'+psa_id+'/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)
		try:
			plug=M2L_Plugin.objects.get(plugin_id=PSA.objects.get(psa_id=psa_id).plugin_id)
			if 'name' in request.query_params:
				plug.name=request.query_params['name']
			if 'url' in request.query_params:
                                plug.url=request.query_params['url']
			plug.save()
			logging.info('%s %s: 200 OK',request.method,'/v1/M2Lplugins/'+psa_id+'/')
			logging.debug('Request params: %s',str(request.query_params))
			
			return Response(status=status.HTTP_200_OK)

		except ObjectDoesNotExist:
	                logging.warning('%s %s: 404 NOT FOUND',request.method,request.get_full_path)
			return Response(status=status.HTTP_404_NOT_FOUND)
class PSARLView(APIView):
	def put(self,request,PSARL_id):
		"""
		Updates the location of a Local PSAR. The new location is provided with the argument 'location'
		If there is no PSARL with id=PSARL_id, creates one with the specified location
		token -- (NOT required)
		location -- (required)
		"""

                if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/PSARLs/'+PSARL_id+'/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)


		if 'location' in request.query_params:
			try:
				a=PSAR_local.objects.get(psarl_id=PSARL_id)
			except ObjectDoesNotExist:
				psarl=PSAR_local(psarl_id=PSARL_id,location=request.query_params['location'])
				psarl.save()
		                logging.info('%s %s: 201 CREATED',request.method,'/v1/PSARLs/'+PSARL_id+'/?location='+request.query_params['location'])
				return Response(status=status.HTTP_201_CREATED)
			else:
				a.location=request.query_params['location']
				a.save()
		                logging.info('%s %s: 200 OK',request.method,'/v1/PSARLs/'+PSARL_id+'/?location='+request.query_params['location'])
				return Response(status=status.HTTP_200_OK)

		else:
	                logging.warning('%s %s: 400 BAD REQUEST',request.method,'/v1/PSARLs/'+PSARL_id+'/')
			return Response(status=status.HTTP_400_BAD_REQUEST)
			
class PSAImageLocationView(APIView):
	def get(self, request, psa_id):
		"""
		Gets the URL where to download the image of the PSA with id=psa_id
		token -- (NOT required)
		"""

                if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/PSA/images/'+psa_id+'/image_location')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)


		try:
			psa=PSA.objects.get(psa_id=psa_id)
			sto=PSA_storage.objects.get(psa_storage_id=psa.psa_storage_id)
		        logging.info('%s %s: 200 OK',request.method,'/v1/PSA/images/'+psa_id+'/image_location')
			return Response(sto.url,status=status.HTTP_200_OK)
		except ObjectDoesNotExist:
	                logging.warning('%s %s: 404 NOT FOUND',request.method,'/v1/PSA/images/'+psa_id+'/image_location')
			return Response(status=status.HTTP_404_NOT_FOUND)
		



class M2LPluginLocationView(APIView):
	def get(self, request, psa_id):
		"""
		Gets the URL where to download the M2L Plugin of the PSA with id=psa_id
		token -- (NOT required)
		"""


                if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/PSA/M2Lplugins/'+psa_id+'/plugin_location')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)

		try:
			psa=PSA.objects.get(psa_id=psa_id)
			plug=M2L_Plugin.objects.get(plugin_id=psa.plugin_id)
	                logging.info('%s %s: 200 OK',request.method,'/v1/PSA/M2Lplugins/'+psa_id+'/plugin_location')
			return Response(plug.url,status=status.HTTP_200_OK)
		except ObjectDoesNotExist:
	                logging.warning('%s %s: 404 NOT FOUND',request.method,'/v1/PSA/M2Lplugins/'+psa_id+'/plugin_location')
			return Response(status=status.HTTP_404_NOT_FOUND)

class PSADynConfView(APIView):
	def get(self, request, psa_id):

		"""
		Returns JSON with the base64 specific dynamic (frequently changeable) configuration of a PSA and the parameter per country.

		token -- (NOT required)
		location -- (required)

		"""
		if not check_token(request):
			logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/PSA/images/'+psa_id+'/dyn_conf')
			return Response(status=status.HTTP_401_UNAUTHORIZED)
		if 'location' in request.query_params:
			try:
				psa=PSA.objects.get(psa_id=psa_id)
				psa= dynamic_Conf.objects.get(psa=psa_id, location=request.query_params['location'])
        	        	serial = dynamic_ConfSerializer(psa)
        		        logging.info('%s %s: 200 OK',request.method,'/v1/PSA/dyn_conf/'+psa_id+'/'+request.query_params['location']+'/')
                        	return Response (status=status.HTTP_200_OK,data=serial.data)
			except ObjectDoesNotExist:
				logging.warning('%s %s: 404 NOT FOUND',request.method,'/v1/PSA/dyn_conf/'+psa_id+'/')
				return Response(status=status.HTTP_404_NOT_FOUND)
		else:
                        logging.warning('%s %s: 400 BAD REQUEST ',request.method, '/v1/PSA/images/'+psa_id+'/dyn_conf/')
			return Response(status=status.HTTP_400_BAD_REQUEST)



        def put(self, request, psa_id):
                """
		Create or update an entry in the dynamic configuration table for a PSA

		token -- (NOT required)
		location -- (required)
		dyn_conf -- (required)
                """
                if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/PSA/dyn_conf/'+psa_id+'/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)
		if 'location' in request.query_params:
			pass
		if 'dyn_conf' in request.query_params:
			try:
				psa=PSA.objects.get(psa_id=psa_id)
				try:
		        		psa= dynamic_Conf.objects.get(psa=psa_id, location=request.query_params['location'])
                			psa.dyn_conf = request.query_params['dyn_conf']
                       			psa.save()
					serial = dynamic_ConfSerializer(psa)
		    	        	logging.info('%s %s: 200 OK',request.method,'/v1/PSA/dyn_conf/'+psa_id+'/')
        	        	       	return Response(status=status.HTTP_200_OK, data=serial.data)
				except:
					psa=dynamic_Conf(psa=psa_id, location=request.query_params['location'], dyn_conf=request.query_params['dyn_conf'])
	        	                psa.save()
        	       			serial = dynamic_ConfSerializer(psa)
	                	        logging.info('%s %s: 201 CREATED',request.method, '/v1/psar/dyn_conf/'+psa_id+'/')       		     
		   	        	logging.debug('Request data: %s',request.data)
               			        logging.debug('Response data: %s',serial.data)
                       			return Response(status=status.HTTP_201_CREATED,data=serial.data)
       	        	except ObjectDoesNotExist:
                        	logging.warning('%s %s: 404 NOT FOUND',request.method,'/v1/PSA/images/'+psa_id+'/')
               	        	return Response(status=status.HTTP_404_NOT_FOUND)
		else:
                        logging.warning('%s %s: 400 BAD REQUEST ',request.method, '/v1/PSA/images/'+psa_id+'/dyn_conf/')
			return Response(status=status.HTTP_400_BAD_REQUEST)



	def delete (self, request, psa_id):
		"""
		Deletes the specific dynamic configuration for a PSA.

		token -- (NOT required)
		location -- (required)

		"""
                if not check_token(request):
                        logging.warning('%s %s: 401 UNAUTHORIZED',request.method,'/v1/PSA/dyn_conf/'+psa_id+'/')
                        return Response(status=status.HTTP_401_UNAUTHORIZED)
		if 'location' in request.query_params:
			try:
				psa=PSA.objects.get(psa_id=psa_id)
				psa = dynamic_Conf.objects.get(psa=psa_id, location=request.query_params['location'])
				psa.delete()
		                logging.info('%s %s: 204 NO CONTENT',request.method,'/v1/PSA/dyn_conf/'+psa_id+'/')
				return Response (status=status.HTTP_204_NO_CONTENT)
			except ObjectDoesNotExist:
		                logging.warning('%s %s: 404 NOT FOUND',request.method,'/v1/PSA/dyn_conf/'+psa_id+'/')
				return Response(status=status.HTTP_404_NOT_FOUND)
		else:
                        logging.warning('%s %s: 400 BAD REQUEST ',request.method, '/v1/PSA/images/'+psa_id+'/dyn_conf/')
			return Response(status=status.HTTP_400_BAD_REQUEST)



def parseBoolString(B):	
	# Handle case where b is already a Boolean type.
	b = B.lower()

	if b == 'false':
		return False
	elif b == 'true':
		return True
	else:
		return None
