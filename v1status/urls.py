from django.conf.urls import url
from v1status import views

urlpatterns = [ 
	url(r'^v1/status$', views.v1status),
]
