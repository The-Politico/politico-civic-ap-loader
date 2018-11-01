from django.core.management.base import BaseCommand

from aploader.models import ChamberCall
from election.models import ElectionCycle
from government.models import Body


class Command(BaseCommand):
    help = "Sets up model objects for chamber calls"

    def handle(self, *args, **options):
        cycle = ElectionCycle.objects.get(slug="2018")
        house = Body.objects.get(slug="house")
        senate = Body.objects.get(slug="senate")

        ChamberCall.objects.get_or_create(cycle=cycle, body=house)
        ChamberCall.objects.get_or_create(cycle=cycle, body=senate)
