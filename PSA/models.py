from django.db import models
class PSA (models.Model):
	psa_id = models.CharField(unique=True,max_length=100)
	psa_name = models.CharField(unique=True,max_length=100, blank=False)
	psa_status = models.PositiveSmallIntegerField()
	psa_manifest_id = models.CharField(unique=True,max_length=100)
	psa_storage_id = models.CharField(max_length=100)
	plugin_id = models.CharField(unique=True,max_length=100)
	psa_image_hash = models.CharField(max_length=100, default = '')
	psa_description = models.CharField(max_length=200, default='')
	is_generic = models.BooleanField(default=False)
	owner = models.CharField(max_length=100, default='')
	image_id = models.CharField(max_length=100, default='')
	cost = models.FloatField(default=0)
	latency = models.FloatField(default=0)
	rating = models.FloatField(default=0)

class Capability(models.Model):
	capability=models.CharField(max_length=100,primary_key=True)

class PSACapabilityAssociation(models.Model):
	#psa = models.ForeignKey('PSA')
	psa = models.CharField(max_length=100,blank=False)
	capability = models.CharField(max_length=100)

class PSA_manifest(models.Model):
	psa_manifest_id= models.CharField(primary_key=True,max_length=100)
	name = models.CharField(max_length=100, blank=False, default = 'New Manifest')
	general_info_id = models.CharField(max_length=100)
	funcionality_id = models.CharField(max_length=100)
	execution_model_id = models.CharField(max_length=100)
	configuration_id = models.CharField(max_length=100)
	monitoring_id = models.CharField(max_length=100)
	custom_id = models.CharField(max_length=100)

class M2L_Plugin(models.Model):
	plugin_id = models.CharField(primary_key=True,max_length=100)
	name=models.CharField(max_length=100, blank=False, default = 'New M2L')
	url=models.URLField()

class PSA_storage(models.Model):
	psa_storage_id=models.CharField(primary_key=True,max_length=100)
	name=models.CharField(max_length=100, blank=False, default = "NEW Storage")
	psarl_id=models.CharField(max_length=100)
	url=models.URLField()

class PSAR_local(models.Model):	
	psarl_id=models.CharField(primary_key=True,max_length=100)
	location =models.CharField(max_length=100, blank=False)

class dynamic_Conf(models.Model):
	#psa = models.ForeignKey('PSA',blank=True)
	psa = models.CharField(max_length=100,blank=False)
	location = models.CharField(max_length=100)
	dyn_conf = models.CharField(max_length=60000)
        timestamp = models.DateTimeField(auto_now=True)	
	id= models.AutoField(primary_key=True)

