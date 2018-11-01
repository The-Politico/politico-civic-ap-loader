from aploader.models import ChamberCall
from rest_framework import serializers


class ChamberCallSerializer(serializers.ModelSerializer):
    body = serializers.SerializerMethodField()
    cycle = serializers.SerializerMethodField()
    party = serializers.SerializerMethodField()

    def get_body(self, obj):
        return obj.body.slug

    def get_cycle(self, obj):
        return obj.cycle.slug

    def get_party(self, obj):
        if obj.party:
            return obj.party.ap_code
        else:
            return None

    class Meta:
        model = ChamberCall
        fields = ["body", "cycle", "party"]
