from django.test import TestCase, Client
from rest_framework import status
import views

class StatusTestCase(TestCase):

	def testStatus(self):
		client = Client()
		views.auth=True
		response=client.get("/v1/status")
		self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)
		views.auth=False
		resp=client.get("/v1/status")
		self.assertEquals(resp.status_code, status.HTTP_200_OK)
		views.auth=True
	

