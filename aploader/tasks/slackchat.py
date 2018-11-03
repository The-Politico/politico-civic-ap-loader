from argparse import Namespace

from celery import shared_task
from django.conf import settings
from slackclient import SlackClient

from aploader.models import APElectionMeta

SLACK_BOT_TOKEN = getattr(settings, "CIVIC_SLACK_BOT_TOKEN", None)


def get_client():
    if SLACK_BOT_TOKEN:
        return SlackClient(SLACK_BOT_TOKEN)
    return None


def format_party(party):
    lp = party.lower()
    if lp == "gop":
        return "R"
    if lp == "dem":
        return "D"
    return "I"


@shared_task
def call_race_in_slackchat(payload):
    payload = Namespace(**payload)

    # FORMAT LIKE...
    #
    # RACE CALL
    # *Texas Governor*
    # Called for First Last |(D)| |link|

    if payload.runoff:
        return

    ap_meta = APElectionMeta.objects.get(
        ap_election_id=payload.race_id,
        election__election_day__slug=payload.election_date,
    )

    # Get race rating
    race_rating = ap_meta.election.race.ratings.latest("created_date")
    rating_code = race_rating.category.order

    # Skip races that were solid and called correctly
    if rating_code == 1 and format_party(payload.candidate_party) == "D":
        return
    if rating_code == 7 and format_party(payload.candidate_party) == "R":
        return

    client = get_client()

    bot_channel = getattr(
        settings, "CIVIC_SLACKCHAT_CHANNEL_NAME", "slackchat-elex-test"
    )
    text = "RACE CALL\n*{}*\nCalled for {} |({})| | `{}` |".format(
        payload.office_short,
        payload.candidate,
        format_party(payload.candidate_party),
        payload.page_url,
    )

    client.api_call(
        "chat.postMessage", channel=bot_channel, text=text, as_user=True
    )
