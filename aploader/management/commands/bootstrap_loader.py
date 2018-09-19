from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Bootstrap development."

    def handle(self, *args, **options):
        call_command("bootstrap_geography")
        call_command("bootstrap_jurisdictions")
        call_command("bootstrap_fed")
        call_command("bootstrap_offices")
        call_command("bootstrap_parties")
        call_command("bootstrap_election_events")
        call_command("bootstrap_elections")
        call_command("bootstrap_specials")
        call_command("initialize_election_date", "2018-11-06", "--test")
