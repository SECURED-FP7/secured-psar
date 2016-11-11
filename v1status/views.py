from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from keystoneclient.v2_0 import client
from keystoneclient.exceptions import AuthorizationFailure, Unauthorized


YOUR_IP = '10.95.51.188'
ADMIN_USER ='admin'
ADMIN_PASS = 'psardev1234'

auth=False

def check_token(request):
        
	if not auth:
		return True
	
	if 'auth_token' in request.query_params:
                auth_token = request.query_params['auth_token']
                admin_client = client.Client(username=ADMIN_USER, auth_url='http://'+str(YOUR_IP) +':35357/v2.0', password=ADMIN_PASS)
                try:
                        auth_result = admin_client.tokens.authenticate(token=auth_token)
                        if not auth_result:
                                return False

			return True
                except Unauthorized as unauth:
                       return False
        else:
                return False



class v1Status(APIView):
	"""
	Dummy. If the server is up, returns HTTP code 200
	"""
	def get(self,request):
		var =check_token(request) 
		if not var:		
			return Response(status=status.HTTP_401_UNAUTHORIZED)
		return Response(status=status.HTTP_200_OK)
