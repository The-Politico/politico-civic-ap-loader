import json
import sys
from datetime import datetime
from time import sleep

from almanac.models import ElectionEvent
from aploader.celery import (
    call_race_in_slack,
    call_race_on_twitter,
    bake_notifications,
)
from aploader.conf import settings as app_settings
from aploader.models import APElectionMeta
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from election.models import Candidate, CandidateElection
from geography.models import Division, DivisionLevel
from tqdm import tqdm
from vote.models import Votes

from .utils.notifications.formatters import format_office_label


class Command(BaseCommand):
    help = (
        "Ingests master results JSON file from Elex and updates the results "
        "models in Django."
    )

    def load_results(self, level):
        data = None
        while data is None:
            try:
                data = json.load(open("reup_{}.json".format(level)))
            except json.decoder.JSONDecodeError:
                print("Waiting for file to be available.")
                sleep(5)
        return data

    def deconstruct_result(self, result):
        keys = [
            "id",
            "raceid",
            "is_ballot_measure",
            "electiondate",
            "level",
            "statepostal",
            "reportingunitname",
            "last",
            "officename",
            "racetype",
            "winner",
            "uncontested",
            "runoff",
            "votecount",
            "votepct",
            "precinctsreporting",
            "precinctsreportingpct",
            "precinctstotal",
        ]
        return [result[key] for key in keys]

    def process_result(self, result, tabulated, no_bots, election_slug):
        """
        Processes top-level (state) results for candidate races, loads data
        into the database  and sends alerts for winning results.
        """
        # Deconstruct result in variables
        (
            ID,
            RACE_ID,
            IS_BALLOT_MEASURE,
            ELEX_ELECTION_DATE,
            LEVEL,
            STATE_POSTAL,
            REPORTING_UNIT,
            LAST_NAME,
            OFFICE_NAME,
            RACE_TYPE,
            WINNER,
            UNCONTESTED,
            RUNOFF,
            VOTE_COUNT,
            VOTE_PERCENT,
            PRECINCTS_REPORTING,
            PRECINCTS_REPORTING_PERCENT,
            PRECINCTS_TOTAL,
        ) = self.deconstruct_result(result)

        # Skip ballot measures on non-state-level results
        if IS_BALLOT_MEASURE or LEVEL != DivisionLevel.STATE:
            return

        try:
            ap_meta = APElectionMeta.objects.get(
                ap_election_id=RACE_ID,
                election__election_day__slug=election_slug,
            )
        except ObjectDoesNotExist:
            print(
                "No AP Meta found for {0} {1} {2}".format(
                    LAST_NAME, OFFICE_NAME, REPORTING_UNIT
                )
            )
            return

        id_components = ID.split("-")
        CANDIDATE_ID = "{0}-{1}".format(id_components[1], id_components[2])
        if LAST_NAME == "None of these candidates":
            CANDIDATE_ID = "{0}-{1}".format(id_components[0], CANDIDATE_ID)

        try:
            candidate_election = CandidateElection.objects.get(
                election=ap_meta.election,
                candidate__ap_candidate_id=CANDIDATE_ID,
            )
        except ObjectDoesNotExist:
            print(
                "No Candidate found for {0} {1} {2}".format(
                    LAST_NAME, OFFICE_NAME, REPORTING_UNIT
                )
            )
            return

        candidate = candidate_election.candidate

        division = Division.objects.get(
            level__name=DivisionLevel.STATE,
            code_components__postal=STATE_POSTAL,
        )

        filter_kwargs = {
            "candidate_election": candidate_election,
            "division": division,
        }

        vote_update = {}

        if not ap_meta.override_ap_votes:
            vote_update["count"] = VOTE_COUNT
            vote_update["pct"] = VOTE_PERCENT

        if not ap_meta.override_ap_call:
            vote_update["winning"] = WINNER
            vote_update["runoff"] = RUNOFF

        if ap_meta.precincts_reporting != PRECINCTS_REPORTING:
            ap_meta.precincts_reporting = PRECINCTS_REPORTING
            ap_meta.precincts_total = PRECINCTS_TOTAL
            ap_meta.precincts_reporting_pct = PRECINCTS_REPORTING_PERCENT

        if PRECINCTS_REPORTING_PERCENT == 1 or UNCONTESTED or tabulated:
            ap_meta.tabulated = True
        else:
            ap_meta.tabulated = False

        ap_meta.save()

        votes = Votes.objects.filter(**filter_kwargs)

        if (WINNER or RUNOFF) and not candidate_election.uncontested:
            # If new call on contested race, send alerts
            first = votes.first()

            if not (first.winning or first.runoff) and not no_bots:
                if ap_meta.election.party:
                    PARTY = ap_meta.election.party.label
                else:
                    PARTY = None

                # construct page URL for payload
                if app_settings.AWS_S3_BUCKET == "interactives.politico.com":
                    base_url = "https://www.politico.com/election-results/2018"
                    end_path = ""
                else:
                    base_url = "https://s3.amazonaws.com/staging.interactives.politico.com/election-results/2018"  # noqa
                    end_path = "index.html"

                if RACE_TYPE == "Runoff":
                    state_path = "{}/runoff".format(division.slug)
                elif "Special" in RACE_TYPE:
                    # first check to see if this special is on a state page
                    events = ElectionEvent.objects.filter(
                        division=division,
                        election_day__slug=ELEX_ELECTION_DATE,
                    )
                    print(events, division, ELEX_ELECTION_DATE)

                    if len(events) > 0:
                        state_path = division.slug
                    else:
                        parsed = datetime.strptime(
                            ELEX_ELECTION_DATE, "%Y-%m-%d"
                        )
                        month = parsed.strftime("%b").lower()
                        day = parsed.strftime("%d")

                        state_path = "{}/special-election/{}-{}".format(
                            division.slug, month, day
                        )
                else:
                    state_path = division.slug

                url = "{}/{}/{}".format(base_url, state_path, end_path)

                payload = {
                    "race_id": RACE_ID,
                    "division": division.label,
                    "division_slug": division.slug,
                    "office": format_office_label(
                        candidate.race.office, division.label
                    ),
                    "candidate": "{} {}".format(
                        candidate.person.first_name, candidate.person.last_name
                    ),
                    "primary_party": PARTY,
                    "vote_percent": VOTE_PERCENT,
                    "vote_count": VOTE_COUNT,
                    "runoff": RUNOFF,
                    "precincts_reporting_percent": PRECINCTS_REPORTING_PERCENT,
                    "jungle": RACE_TYPE == "Open Primary",
                    "runoff_election": RACE_TYPE == "Runoff",
                    "special_election": "Special" in RACE_TYPE,
                    "page_url": url,
                }
                call_race_in_slack.delay(payload)
                call_race_on_twitter.delay(payload)
                self.calls.append(payload)

        votes.update(**vote_update)

    def main(self, options):
        TABULATED = options["tabulated"]
        PASSED_ELECTION_DATE = options["election_date"]
        LEVEL = options["level"]
        RUN_ONCE = options["run_once"]
        NO_BOTS = options["no_bots"]
        INTERVAL = app_settings.DATABASE_UPLOAD_DAEMON_INTERVAL

        while True:
            results = self.load_results(LEVEL)
            self.calls = []

            for result in tqdm(results):
                self.process_result(
                    result, TABULATED, NO_BOTS, PASSED_ELECTION_DATE
                )

            if len(self.calls) > 0:
                bake_notifications(self.calls)

            if RUN_ONCE:
                print("Run once specified, exiting.")
                sys.exit(0)

            sleep(INTERVAL)

    def add_arguments(self, parser):
        parser.add_argument("election_date", type=str)
        parser.add_argument("level", type=str)
        parser.add_argument("--run_once", dest="run_once", action="store_true")
        parser.add_argument(
            "--tabulated", dest="tabulated", action="store_true"
        )
        parser.add_argument("--nobots", dest="no_bots", action="store_true")

    def handle(self, *args, **options):
        self.main(options)
