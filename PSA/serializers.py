from django.forms import widgets
from rest_framework import serializers
from models import PSA_manifest, PSA, PSACapabilityAssociation, M2L_Plugin, PSA_storage, PSAR_local, Capability, dynamic_Conf

class PSASerializer(serializers.ModelSerializer):
	class Meta:
		model=PSA
class PSACapabilityAssociationSerializer(serializers.ModelSerializer):
	class Meta:
		model=PSACapabilityAssociation
		fields=('psa','capability')
class CapabilitySerializer(serializers.ModelSerializer):
	class Meta:
		model=Capability

class M2LPluginSerializer(serializers.ModelSerializer):
	class Meta:
		model=M2L_Plugin

class PSASerializerMini(serializers.ModelSerializer):
	class Meta:
		model=PSA
		fields=('psa_id','psa_name')


class PSAManifestSerializer(serializers.ModelSerializer):
	class Meta:
		model=PSA_manifest
class PSAStorageSerializer(serializers.ModelSerializer):
	class Meta:
		model=PSA_storage

class PSARLocalSerializer(serializers.ModelSerializer):
	class Meta:
		model=PSAR_local              	


class PSAOptimizationParameterSerializer(serializers.ModelSerializer):
        class Meta:
                model=PSA
		fields=('cost','latency','rating')

class dynamic_ConfSerializer(serializers.ModelSerializer):
	class Meta:
		model=dynamic_Conf
		fields=('psa','location','dyn_conf','timestamp')
