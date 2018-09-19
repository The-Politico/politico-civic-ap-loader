from aploader.models import APElectionMeta
from rest_framework import serializers


class APElectionMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = APElectionMeta
        fields = "__all__"
