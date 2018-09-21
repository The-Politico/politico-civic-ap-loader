from aploader.models import APElectionMeta
from election.models import Candidate, Election
from entity.models import Person
from geography.models import DivisionLevel
from government.models import Party
from vote.models import Votes
from rest_framework import serializers


class VotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Votes
        fields = ("count", "pct", "winning", "runoff")


class CandidateSerializer(serializers.ModelSerializer):
    votes = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    party = serializers.SerializerMethodField()

    def get_votes(self, obj):
        election = Election.objects.get(
            race=obj.race, election_day__slug="2018-11-06"
        )
        votes = obj.get_election_votes(election).filter(
            division__level__name=DivisionLevel.STATE
        )[0]
        return VotesSerializer(votes).data

    def get_name(self, obj):
        return obj.person.full_name

    def get_party(self, obj):
        return obj.party.label

    class Meta:
        model = Candidate
        fields = ("ap_candidate_id", "name", "party", "votes")


class ElectionSerializer(serializers.ModelSerializer):
    office = serializers.SerializerMethodField()
    candidates = serializers.SerializerMethodField()
    body = serializers.SerializerMethodField()

    def get_office(self, obj):
        return obj.race.office.label

    def get_body(self, obj):
        if obj.race.office.body:
            return obj.race.office.body.slug
        else:
            return "governor"

    def get_candidates(self, obj):
        return CandidateSerializer(obj.get_candidates(), many=True).data

    class Meta:
        model = Election
        fields = ("office", "body", "candidates")


class APElectionMetaSerializer(serializers.ModelSerializer):
    election = serializers.SerializerMethodField()

    def get_election(self, obj):
        return ElectionSerializer(obj.election).data

    class Meta:
        model = APElectionMeta
        fields = (
            "ap_election_id",
            "called",
            "tabulated",
            "override_ap_call",
            "override_ap_votes",
            "precincts_reporting",
            "precincts_total",
            "precincts_reporting_pct",
            "election",
        )
