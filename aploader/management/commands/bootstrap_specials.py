import csv
import os

from django.core.management.base import BaseCommand

from election.models import (
    Election,
    Race,
    ElectionDay,
    ElectionType,
    ElectionCycle,
)
from geography.models import Division, DivisionLevel
from government.models import Office


class Command(BaseCommand):
    help = "Sets up races and elections for known specials in the general"

    def get_division(self, state, district=None):
        if district:
            return Division.objects.get(
                level__name=DivisionLevel.DISTRICT,
                code=district,
                parent__code=state,
            )
        else:
            return Division.objects.get(
                level__name=DivisionLevel.STATE, code=state
            )

    def get_election_day(self):
        return ElectionDay.objects.get(date="2018-11-06")

    def get_election_type(self):
        return ElectionType.objects.get(slug="general")

    def get_office(self, division, label):
        return Office.objects.get(division=division, label=label)

    def get_election_cycle(self):
        return ElectionCycle.objects.get(slug="2018")

    def get_or_create_race(self, office, cycle):
        race, created = Race.objects.get_or_create(
            office=office, special=True, cycle=cycle
        )
        return race

    def get_or_create_election(
        self, race, election_day, election_type, division
    ):
        Election.objects.get_or_create(
            race=race,
            election_day=election_day,
            election_type=election_type,
            division=division,
        )

    def handle(self, *args, **options):
        cmd_path = os.path.dirname(os.path.realpath(__file__))
        csv_path = os.path.join(cmd_path, "../../bin/specials.csv")

        election_day = self.get_election_day()
        election_type = self.get_election_type()
        election_cycle = self.get_election_cycle()

        with open(csv_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                division = self.get_division(row["state"], row["district"])
                office = self.get_office(division, row["office"])
                race = self.get_or_create_race(office, election_cycle)

                self.get_or_create_election(
                    race, election_day, election_type, division
                )
