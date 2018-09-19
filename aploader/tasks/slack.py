import time
from argparse import Namespace

from celery import shared_task
from django.conf import settings
from aploader.conf import settings as app_settings
from slacker import Slacker

SLACK_TOKEN = getattr(settings, "CIVIC_SLACK_TOKEN", None)


def get_client():
    if SLACK_TOKEN:
        return Slacker(SLACK_TOKEN)
    return None


@shared_task
def call_race_in_slack(payload):
    payload = Namespace(**payload)

    if payload.runoff:
        WINNING = "✓ *{}* (advances to a runoff)".format(payload.candidate)
    else:
        WINNING = "✓ *{}*".format(payload.candidate)

    attachment_data = [
        {
            "fallback": "🚨 Race called in *{}*".format(
                payload.division.upper()
            ),
            "color": "#6DA9CC",
            "pretext": "<!here|here> :rotating_light: Race called in *{}*".format(
                payload.division.upper()
            ),
            "mrkdwn_in": ["fields"],
            "author_name": "Election Bot",
            "author_icon": "https://pbs.twimg.com/profile_images/998954486205898753/gbb2psb__400x400.jpg",  # noqa
            "title": "Winner for {}".format(payload.office),
            "title_link": payload.page_url,
            "text": WINNING,
            "footer": "Associated Press",
            "fields": [
                {
                    "title": "Winning vote",
                    "value": "{}% | {:,} votes".format(
                        int(round(payload.vote_percent * 100)),
                        int(payload.vote_count),
                    ),
                    "short": True,
                },
                {
                    "title": "Precincts reporting",
                    "value": "{}%".format(
                        int(round(payload.precincts_reporting_percent * 100))
                    ),
                    "short": True,
                },
            ],
            "ts": int(time.time()),
        }
    ]

    client = get_client()

    if app_settings.AWS_S3_BUCKET == "interactives.politico.com":
        channel = "#elections-bot"
    else:
        channel = "#elections-bot-stg"

    client.chat.post_message(
        channel,
        "",
        attachments=attachment_data,
        as_user=False,
        username="Elections Bot",
    )
