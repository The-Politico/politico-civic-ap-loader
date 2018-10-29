from django.db import models
from election.models import ElectionCycle
from government.models import Body, Party


class ChamberCall(models.Model):
    """
    Calls for chambers of Congress
    """

    body = models.ForeignKey(
        Body, related_name="calls", on_delete=models.CASCADE
    )
    cycle = models.ForeignKey(
        ElectionCycle, related_name="chamber_calls", on_delete=models.CASCADE
    )
    party = models.ForeignKey(
        Party,
        related_name="chamber_calls",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    call_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.body.label
