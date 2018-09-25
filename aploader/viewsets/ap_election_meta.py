from aploader.models import APElectionMeta
from aploader.serializers import APElectionMetaSerializer
from election.models import Candidate
from entity.conf import settings
from entity.utils.importers import import_class
from geography.models import DivisionLevel
from rest_framework.views import APIView
from rest_framework.response import Response

authentication = import_class(settings.API_AUTHENTICATION_CLASS)
permission = import_class(settings.API_PERMISSION_CLASS)


class APElectionMetaList(APIView):
    authentication_classes = (authentication,)
    permission_classes = (permission,)
    serializer_class = APElectionMetaSerializer

    def get(self, request, state):
        statewides = APElectionMeta.objects.filter(
            election__division__slug=state
        )
        districts = APElectionMeta.objects.filter(
            election__division__parent__slug=state
        )

        elections = statewides | districts
        data = APElectionMetaSerializer(elections, many=True).data
        return Response(data)

    def post(self, request, state):
        meta = APElectionMeta.objects.get(
            ap_election_id=request.data["ap_election_id"]
        )

        if request.data.get("override") is not None:
            meta.override_ap_call = request.data["override"]

        if request.data.get("called") is not None:
            meta.called = request.data["called"]

        meta.save()

        if (
            request.data.get("ap_candidate_id")
            and request.data.get("winner") is not None
        ):
            for candidate in meta.election.get_candidates():
                state_votes = candidate.get_election_votes(
                    meta.election
                ).filter(division__level__name=DivisionLevel.STATE)[0]
                state_votes.winning = False
                state_votes.save()

            winner = Candidate.objects.get(
                ap_candidate_id=request.data["ap_candidate_id"],
                race=meta.election.race,
            )

            votes = winner.get_election_votes(meta.election).filter(
                division__level__name=DivisionLevel.STATE
            )[0]

            votes.winning = request.data["winner"]
            votes.save()

        return Response(200)
