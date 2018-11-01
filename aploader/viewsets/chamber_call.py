from aploader.models import ChamberCall
from aploader.serializers import ChamberCallSerializer
from election.models import ElectionCycle
from government.models import Body, Party
from entity.conf import settings
from entity.utils.importers import import_class
from geography.models import DivisionLevel
from rest_framework.views import APIView
from rest_framework.response import Response

authentication = import_class(settings.API_AUTHENTICATION_CLASS)
permission = import_class(settings.API_PERMISSION_CLASS)


class ChamberCallList(APIView):
    authentication_classes = (authentication,)
    permission_classes = (permission,)
    serializer_class = ChamberCallSerializer

    def get(self, request):
        calls = ChamberCall.objects.all()
        data = ChamberCallSerializer(calls, many=True).data
        return Response(data)

    def post(self, request):
        body = Body.objects.get(slug=request.data["body"])
        cycle = ElectionCycle.objects.get(slug="2018")
        if request.data.get("party"):
            party = Party.objects.get(ap_code=request.data["party"])
        else:
            party = None
        call = ChamberCall.objects.get(body=body, cycle=cycle)
        call.party = party
        call.save()

        return Response(200)
