#!/usr/bin/python

from requests import get, put, delete, patch, post
import urllib
from keystoneclient.v2_0 import client
import argparse,json,os, subprocess
import psarClient

'''
Client for the PSAR API. All methods return a Response object.

TO-DO: Currently only tested without authentication. 
'''

	
class Client:
	def __init__(self,base_url):
		self.psar_client=psarClient.Client(base_url)
	
	
	def create_psa(self, psa_id, path, name=None):
		self.psar_client.create_psa(id=psa_id,name=name)
		if subprocess.call(['ls',path])!=0:
			print 'Not a valid path'
		else:
			if not path.endswith('/'):
				path=path+'/'
			image_path=path+'image'
			manifest_path=path+'manifest'
			plugin_path=path+'plugin'
			self.psar_client.put_image_file(psa_id=psa_id,path=image_path,disk_format='qcow2',container_format='bare')
			self.psar_client.put_manifest_file(psa_id=psa_id,path=manifest_path)
			self.psar_client.put_plugin_file(psa_id=psa_id,path=plugin_path)
		
		
	



if __name__=='__main__':
	#TO-DO: Take arguments (such as the url of the psar) from environment
	#Functions
	PSAR_URL=os.getenv('PSAR_URL','http://195.235.93.146:8080')

	def create_psa(args):
                if args.url:
                        c=Client(args.url)
                else:
                         c=Client(PSAR_URL)
		if args.name:
			name=args.name
		else:
			name=args.id
		c.create_psa(psa_id=args.id,path=args.path,name=name)
		
	
	#General
	parser=argparse.ArgumentParser(description="Command line client for automatic upload of PSA")
	subparsers = parser.add_subparsers(help='groups')
	
	create_parser=subparsers.add_parser('create',help='Creates a new PSA')
	create_parser.add_argument('id',action='store', help='ID of the PSA')
	create_parser.add_argument('path',action='store', help='Path with the required files')
	create_parser.add_argument('--url',action='store', help='URL of the PSAR')
	create_parser.add_argument('--token',action='store', help='Authentication token')
	create_parser.add_argument('--name',action='store', help='Name')
	create_parser.set_defaults(func=create_psa)
	args= parser.parse_args()
	args.func(args)
