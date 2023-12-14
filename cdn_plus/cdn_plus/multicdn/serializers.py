# serializers.py
from rest_framework import serializers
from cdn_plus.models import Cname

class CnameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cname
        fields = ['id', 'domain', 'alias', 'cname', 'ttl', 'last_modified', 'associated_distribution']
