from django.core.management.base import BaseCommand

from aploader.celery import (call_race_in_slack, call_race_in_slackchat,
                             call_race_on_twitter)


class Command(BaseCommand):
    help = "Sends a test call to Slack/Twitter bots"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        payload = {
            "race_id": "45870",
            "division": "Texas",
            "division_slug": "texas",
            "office": "the Senate in Texas",
            "office_short": "Texas Senate",
            "candidate": "Beto O'Rourke",
            "candidate_party": "Dem",
            "election_date": "2018-11-06",
            "primary_party": None,
            "vote_percent": 0.51,
            "vote_count": 95647,
            "runoff": False,
            "precincts_reporting_percent": 1,
            "jungle": False,
            "runoff_election": False,
            "special_election": False,
            "page_url": "https://s3.amazonaws.com/staging.interactives.politico.com/election-results/2018/texas/index.html",  # noqa
        }
        call_race_in_slack.delay(payload)
        call_race_in_slackchat.delay(payload)
        call_race_on_twitter.delay(payload)
