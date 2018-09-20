import json
import logging
from datetime import datetime

from aploader.utils.aws import defaults, get_bucket
from celery import shared_task

logger = logging.getLogger("tasks")


@shared_task(acks_late=True)
def bake_notifications(calls):
    key = "election-results/2018/notifications.json"
    bucket = get_bucket()
    data = {"timestamp": datetime.now().isoformat(), "calls": calls}
    bucket.put_object(
        Key=key,
        ACL=defaults.ACL,
        Body=json.dumps(data),
        CacheControl=defaults.CACHE_HEADER,
        ContentType="application/json",
    )
