from aploader.celery import (call_race_in_slack, call_race_in_slackchat,
                             call_race_on_twitter)
from aploader.conf import settings as app_settings
from aploader.management.commands.utils.notifications.formatters import (
    format_office_label, short_format_office_label
)
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
        bots = False

        meta = APElectionMeta.objects.get(
            ap_election_id=request.data["ap_election_id"],
            election__election_day__slug="2018-11-06",
        )

        if request.data.get("override") is not None:
            meta.override_ap_call = request.data["override"]

        if request.data.get("called") is not None:
            meta.called = request.data["called"]

        if (
            request.data.get("ap_candidate_id")
            and request.data.get("winner") is not None
        ):
            if (request.data["winner"]):
                bots = True

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

        meta.save()

        if bots:
            if app_settings.AWS_S3_BUCKET == "interactives.politico.com":
                base_url = "https://www.politico.com/election-results/2018"
                end_path = ""
            else:
                base_url = "https://s3.amazonaws.com/staging.interactives.politico.com/election-results/2018"  # noqa
                end_path = "index.html"

            if winner.race.office.body.slug == 'house':
                state = winner.race.office.division.parent
            else:
                state = winner.race.office.division

            state_path = state.slug
            url = "{}/{}/{}".format(base_url, state_path, end_path)

            payload = {
                "race_id": meta.ap_election_id,
                "division": state.label,
                "division_slug": state.slug,
                "office": format_office_label(
                    winner.race.office,
                    state.label
                ),
                "office_short": short_format_office_label(
                    winner.race.office,
                    state.label
                ),
                "candidate": "{} {}".format(
                    winner.person.first_name, winner.person.last_name
                ),
                "election_date": "2018-11-06",
                "candidate_party": winner.party.ap_code,
                "primary_party": None,
                "vote_percent": votes.pct,
                "vote_count": votes.count,
                "runoff": votes.runoff,
                "precincts_reporting_percent": meta.precincts_reporting_pct,
                "jungle": False,
                "runoff_election": False,
                "special_election": meta.election.race.special,
                "page_url": url,
            }

            call_race_in_slack.delay(payload)
            call_race_in_slackchat.delay(payload)
            call_race_on_twitter.delay(payload)

        return Response(200)
