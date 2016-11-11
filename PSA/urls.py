from django.conf.urls import url, include, patterns
from django.contrib import admin
from v1status.views import v1Status
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from PSA import views


urlpatterns =[
        url(r'^docs/', include('rest_framework_swagger.urls')),
        url(r'^v1/status', v1Status.as_view(), name='status'),

	url(r'^v1/admin/', include(admin.site.urls)),
	url(r'^v1/PSA/images/$', views.PSAList.as_view(), name='PSA List'),
	url(r'^v1/PSA/manifest/(?P<psa_id>[^/]+)/$', views.PSAManifestView.as_view(), name='Manifest'),
	url(r'^v1/PSA/manifest/(?P<psa_id>[^/]+)/file$', views.PSAManifestFileView.as_view(), name='Manifest File'),
	url(r'^v1/PSA/images/(?P<psa_id>[^/]+)/$', views.PSAView.as_view(), name='PSA Image'),	
	url(r'^v1/PSA/images/(?P<psa_id>[^/]+)/file$', views.PSAFileView.as_view(), name='PSA Image File'),	
	url(r'^v1/PSA/M2Lplugins/(?P<psa_id>[^/]+)/$', views.M2LView.as_view(),name= 'M2L Plugin'),
	url(r'^v1/PSA/M2Lplugins/(?P<psa_id>[^/]+)/file$', views.M2LFileView.as_view(), name= 'M2L Plugin File'),
	url(r'^v1/PSA/M2Lplugins/(?P<psa_id>[^/]+)/plugin_location$', views.M2LPluginLocationView.as_view()),
	url(r'^v1/PSARLs/(?P<PSARL_id>[^/]+)/$', views.PSARLView.as_view(),name='PSARLs'),
	url(r'^v1/PSA/images/(?P<psa_id>[^/]+)/image_location$', views.PSAImageLocationView.as_view()),	
	url(r'^v1/PSA/capabilities/(?P<psa_id>[^/]+)/', views.PSACapabilitiesView.as_view()),	
	url(r'^v1/PSA/opt_par/(?P<psa_id>[^/]+)/', views.PSAOptimizationParameter.as_view()),
	url(r'^v1/PSA/dyn_conf/(?P<psa_id>[^/]+)/', views.PSADynConfView.as_view()),	
]

urlpatterns += staticfiles_urlpatterns()
