from aploader.celery import call_race_in_slack, call_race_on_twitter
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Sends a test call to Slack/Twitter bots"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        payload = {
            "race_id": "36037",
            "division": "Ohio",
            "division_slug": "ohio",
            "office": "the House seat in Ohio’s 12th District",
            "candidate": "Danny O'Connor",
            "primary_party": None,
            "vote_percent": 0.50,
            "vote_count": 95647,
            "runoff": False,
            "precincts_reporting_percent": 1,
            "jungle": False,
            "runoff_election": False,
            "special_election": True,
            "page_url": "https://s3.amazonaws.com/staging.interactives.politico.com/election-results/2018/ohio/index.html",  # noqa
        }

        call_race_in_slack.delay(payload)
        call_race_on_twitter.delay(payload)
