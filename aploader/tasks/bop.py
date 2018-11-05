import json
import logging
from datetime import datetime

from aploader.utils.aws import defaults, get_bucket
from celery import shared_task

logger = logging.getLogger("tasks")


@shared_task(acks_late=True)
def bake_bop(bop):
    key = "election-results/2018/balance-of-power.json"
    bucket = get_bucket()
    bucket.put_object(
        Key=key,
        ACL=defaults.ACL,
        Body=json.dumps(bop),
        CacheControl=defaults.CACHE_HEADER,
        ContentType="application/json",
    )
