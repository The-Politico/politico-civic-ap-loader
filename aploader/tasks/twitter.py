import os
from argparse import Namespace
from urllib.parse import urlencode

import requests
import twitter
from celery import shared_task
from django.conf import settings

from aploader.models import APElectionMeta

CONSUMER_KEY = getattr(settings, "CIVIC_TWITTER_CONSUMER_KEY", None)
CONSUMER_SECRET = getattr(settings, "CIVIC_TWITTER_CONSUMER_SECRET", None)
ACCESS_TOKEN_KEY = getattr(settings, "CIVIC_TWITTER_ACCESS_TOKEN_KEY", None)
ACCESS_TOKEN_SECRET = getattr(
    settings, "CIVIC_TWITTER_ACCESS_TOKEN_SECRET", None
)


def format_candidate_party(party):
    lp = party.lower()
    if lp == "gop":
        return "R"
    if lp == "dem":
        return "D"
    return "Ind"


def get_screenshot(race_id, page_url):
    query = urlencode(
        {
            "path": page_url,
            "selector": ".race-table-{}".format(race_id),
            "padding": "5px 0 0 10px",
        }
    )
    root = "http://politico-botshot.herokuapp.com/shoot/?"

    response = requests.get("{}{}".format(root, query))

    folder = os.path.join(settings.BASE_DIR, "images")

    if not os.path.exists(folder):
        os.makedirs(folder)

    with open("{}/{}.png".format(folder, race_id), "wb") as f:
        f.write(response.content)


def construct_status(
    party,
    candidate,
    candidate_party,
    office,
    runoff,
    division_slug,
    jungle,
    runoff_election,
    special_election,
    page_url,
):
    party_labels = {"Democrat": "Democratic", "Republican": "Republican"}

    # determine winning language
    if runoff:
        winning_language = "has advanced to a runoff in the"
    else:
        if jungle:
            winning_language = "has advanced to the general election in the"
        else:
            winning_language = "has won the"

    # determine race type
    if party:
        party_label = party_labels[party]
        if runoff_election:
            race_label = "{} primary runoff".format(party_label)
        elif special_election:
            race_label = "{} special primary".format(party_label)
        else:
            race_label = "{} primary".format(party_label)
    elif jungle:
        race_label = "open primary"
    else:
        if runoff_election:
            race_label = "runoff election"
        elif special_election:
            race_label = "special election"
        else:
            race_label = "race"

    party_code = format_candidate_party(candidate_party)

    if party_code == "D":
        intro = "🔵"
    elif party_code == "R":
        intro = "🔴"
    else:
        intro = "🚨"

    return intro + " {} ({}) {} {} for {}. \n\n{}".format(
        candidate, party_code, winning_language, race_label, office, page_url
    )


def format_party(party):
    lp = party.lower()
    if lp == "gop":
        return "R"
    if lp == "dem":
        return "D"
    return "I"


@shared_task
def call_race_on_twitter(payload):
    payload = Namespace(**payload)

    ap_meta = APElectionMeta.objects.get(
        ap_election_id=payload.race_id,
        election__election_day__slug=payload.election_date
    )

    # Get race rating
    race_rating = ap_meta.election.race.ratings.latest("created_date")
    rating_code = race_rating.category.order
    noncompetitive = False
    # Skip races that were solid and called correctly
    if rating_code == 1 and format_party(payload.candidate_party) == "D":
        noncompetitive = True
    if rating_code == 7 and format_party(payload.candidate_party) == "R":
        noncompetitive = True

    status = construct_status(
        payload.primary_party,
        payload.candidate,
        payload.candidate_party,
        payload.office,
        payload.runoff,
        payload.division_slug,
        payload.jungle,
        payload.runoff_election,
        payload.special_election,
        payload.page_url,
    )

    api = twitter.Api(
        consumer_key=CONSUMER_KEY,
        consumer_secret=CONSUMER_SECRET,
        access_token_key=ACCESS_TOKEN_KEY,
        access_token_secret=ACCESS_TOKEN_SECRET,
    )

    if noncompetitive:
        api.PostUpdate(status=status)
        return
    try:
        get_screenshot(payload.race_id, payload.page_url)

        with open(
            "{}/images/{}.png".format(settings.BASE_DIR, payload.race_id), "rb"
        ) as f:
            media_id = api.UploadMediaSimple(f)

        api.PostUpdate(status=status, media=[media_id])
    except Exception:
        print("BOTSHOT ERROR", Exception)
        api.PostUpdate(status=status)
