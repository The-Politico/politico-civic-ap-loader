import collections
import json
import subprocess

import election.models as election
import entity.models as entity
import geography.models as geography
import government.models as government
import vote.models as vote
from django.core.management.base import BaseCommand
from tqdm import tqdm

from aploader.models import APElectionMeta


class Command(BaseCommand):
    help = "Bootstraps election meta for all elections in AP data."

    def get_division(self, row):
        """
        Gets the Division object for the given row of election results.
        """

        # back out of Alaska county

        if (
            row["level"] == geography.DivisionLevel.COUNTY
            and row["statename"] == "Alaska"
        ):
            print("Do not take the Alaska county level result")
            return None

        kwargs = {"level__name": row["level"]}

        if row["reportingunitname"]:
            name = row["reportingunitname"]
        else:
            name = row["statename"]

        if row["level"] in [
            geography.DivisionLevel.COUNTY,
            geography.DivisionLevel.TOWNSHIP,
        ]:
            kwargs["code"] = row["fipscode"]
        else:
            kwargs["name"] = name

        return geography.Division.objects.get(**kwargs)

    def get_office(self, row, division):
        """
        Gets the Office object for the given row of election results.
        Depends on knowing the division of the row of election results.
        """
        AT_LARGE_STATES = ["AK", "DE", "MT", "ND", "SD", "VT", "WY"]

        if division.level.name not in [
            geography.DivisionLevel.STATE,
            geography.DivisionLevel.COUNTRY,
        ]:
            state = division.parent
        else:
            state = division

        if row["officename"] == "President":
            return government.Office.objects.get(
                label="President", name="President of the United States"
            )
        elif row["officename"] == "Governor":
            jurisdiction = government.Jurisdiction.objects.get(division=state)

            return government.Office.objects.get(
                slug__endswith="governor", jurisdiction=jurisdiction
            )
        elif row["officename"] == "U.S. Senate":
            body = government.Body.objects.get(label="U.S. Senate")
            if row["seatnum"] == "2":
                senate_class = 2
            else:
                senate_class = self.senate_class
            return government.Office.objects.get(
                body=body, division=state, senate_class=senate_class
            )
        elif row["officename"].startswith("U.S. House"):
            body = government.Body.objects.get(
                label="U.S. House of Representatives"
            )

            if row["statepostal"] in AT_LARGE_STATES:
                code = "00"
            else:
                if row["seatnum"]:
                    code = (
                        row["seatnum"].zfill(2)
                        if int(row["seatnum"]) < 10
                        else row["seatnum"]
                    )
                else:
                    seatnum = row["seatname"].split(" ")[1]
                    code = seatnum.zfill(2) if int(seatnum) < 10 else seatnum

            district = state.children.get(
                level__name=geography.DivisionLevel.DISTRICT, code=code
            )
            return government.Office.objects.get(body=body, division=district)

    def get_race(self, row, division):
        """
        Gets the Race object for the given row of election results.

        In order to get the race, we must know the office. This function
        will get the office as well.

        The only way to know if a Race is a special is based on the string
        of the `racetype` field from the AP data.
        """

        office = self.get_office(row, division)

        try:
            return election.Race.objects.get(
                office=office,
                cycle__name=row["electiondate"].split("-")[0],
                special=(
                    (row["seatnum"] == ("2") and office.body.slug == "senate")
                    or (row["racetype"].startswith("Special"))
                ),
            )
        except:
            print(
                "Could not find race for {} {}".format(
                    row["electiondate"].split("-")[0], office.label
                )
            )

    def get_election(self, row, race):
        """
        Gets the Election object for the given row of election results.
        Depends on knowing the Race object.

        If this is the presidential election, this will determine the
        Division attached to the election based on the row's statename.

        This function depends on knowing the Race object from `get_race`.
        """
        election_day = election.ElectionDay.objects.get(
            date=row["electiondate"]
        )

        if row["racetypeid"] in ["D", "E"]:
            party = government.Party.objects.get(ap_code="Dem")
        elif row["racetypeid"] in ["R", "S"]:
            party = government.Party.objects.get(ap_code="GOP")
        else:
            party = None

        if row["racetype"] == "Runoff" and party:
            election_type = election.ElectionType.objects.get_or_create(
                slug=election.ElectionType.PRIMARY_RUNOFF,
                label="Primary Runoff",
                number_of_winners=1,
            )[0]

            return election.Election.objects.get_or_create(
                election_type=election_type,
                election_day=election_day,
                division=race.office.division,
                race=race,
                party=party,
            )[0]

        try:
            return election.Election.objects.get(
                election_day=election_day,
                division=race.office.division,
                race=race,
                party=party,
            )
        except:
            print(
                "Could not find election for {0} {1} {2}".format(
                    race, row["party"], row["last"]
                )
            )
            return None

    def get_or_create_party(self, row):
        """
        Gets or creates the Party object based on AP code of the row of
        election data.

        All parties that aren't Democratic or Republican are aggregable.
        """
        if row["party"] in ["Dem", "GOP"]:
            aggregable = False
        else:
            aggregable = True

        defaults = {"label": row["party"], "aggregate_candidates": aggregable}

        party, created = government.Party.objects.get_or_create(
            ap_code=row["party"], defaults=defaults
        )

        return party

    def get_or_create_person(self, row):
        """
        Gets or creates the Person object for the given row of AP data.
        """
        person, created = entity.Person.objects.get_or_create(
            first_name=row["first"], last_name=row["last"]
        )

        return person

    def get_or_create_candidate(self, row, party, race):
        """
        Gets or creates the Candidate object for the given row of AP data.

        In order to tie with live data, this will synthesize the proper
        AP candidate id.

        This function also calls `get_or_create_person` to get a Person
        object to pass to Django.
        """

        person = self.get_or_create_person(row)

        id_components = row["id"].split("-")
        candidate_id = "{0}-{1}".format(id_components[1], id_components[2])

        defaults = {"party": party, "incumbent": row.get("incumbent")}

        if person.last_name == "None of these candidates":
            candidate_id = "{0}-{1}".format(id_components[0], candidate_id)

        candidate, created = election.Candidate.objects.update_or_create(
            person=person,
            race=race,
            ap_candidate_id=candidate_id,
            defaults=defaults,
        )

        return candidate

    def get_or_create_candidate_election(
        self, row, election, candidate, party
    ):
        """
        For a given election, this function updates or creates the
        CandidateElection object using the model method on the election.
        """
        return election.update_or_create_candidate(
            candidate, party.aggregate_candidates, row["uncontested"]
        )

    def get_or_create_ap_election_meta(self, row, election):
        """
        Gets or creates the APElectionMeta object for the given row of
        AP data.
        """
        APElectionMeta.objects.get_or_create(
            ap_election_id=row["raceid"], election=election
        )

    def get_or_create_votes(self, row, division, candidate_election):
        """
        Gets or creates the Vote object for the given row of AP data.
        """
        vote.Votes.objects.get_or_create(
            division=division,
            count=row["votecount"],
            pct=row["votepct"],
            winning=row["winner"],
            runoff=row["runoff"],
            candidate_election=candidate_election,
        )

    def process_row(self, row):
        """
        Processes a row of AP election data to determine what model objects
        need to be created.
        """
        division = self.get_division(row)
        if not division:
            return None

        race = self.get_race(row, division)
        election = self.get_election(row, race)
        if not election:
            return None

        party = self.get_or_create_party(row)
        candidate = self.get_or_create_candidate(row, party, race)
        candidate_election = self.get_or_create_candidate_election(
            row, election, candidate, party
        )

        self.get_or_create_ap_election_meta(row, election)
        self.get_or_create_votes(row, division, candidate_election)

    def add_arguments(self, parser):
        parser.add_argument("election_date", type=str)
        parser.add_argument(
            "--senate_class", dest="senate_class", action="store", default="1"
        )
        parser.add_argument("--test", dest="test", action="store_true")

    def handle(self, *args, **options):
        """
        This management command gets data for a given election date from
        elex. Then, it loops through each row of the data and calls
        `process_row`.

        In order for this command to work, you must have bootstrapped all
        of the dependent apps: entity, geography, government, election, vote,
        and almanac.
        """
        self.senate_class = options["senate_class"]

        writefile = open("bootstrap.json", "w")
        elex_args = [
            "elex",
            "results",
            options["election_date"],
            "-o",
            "json",
            "--national-only",
        ]
        if options["test"]:
            elex_args.append("-t")
        subprocess.run(elex_args, stdout=writefile)

        with open("bootstrap.json", "r") as readfile:
            data = json.load(readfile)
            candidates = collections.defaultdict(list)
            for d in data:
                key = "{0} {1}: {2}, {3}".format(
                    d["officename"], d["statename"], d["last"], d["first"]
                )
                candidates[key].append(d)
            for candidate_races in tqdm(
                candidates.values(), desc="Candidates"
            ):
                tqdm.write(
                    "{0} {1}: {2}, {3}".format(
                        candidate_races[0]["statename"],
                        candidate_races[0]["officename"],
                        candidate_races[0]["last"],
                        candidate_races[0]["first"],
                    )
                )
                for race in tqdm(
                    candidate_races, desc="Contests", leave=False
                ):
                    if race["level"] == geography.DivisionLevel.TOWNSHIP:
                        continue
                    # TODO: Check this with Tyler
                    if not race.get("level", None):
                        continue

                    if race["is_ballot_measure"]:
                        continue

                    self.process_row(race)
