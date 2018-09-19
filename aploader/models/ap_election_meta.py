from django.db import models
from election.models import BallotMeasure, Election


class APElectionMeta(models.Model):
    """
    Election information corresponding to AP election night.
    """

    election = models.OneToOneField(
        Election,
        related_name="meta",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    ballot_measure = models.OneToOneField(
        BallotMeasure,
        related_name="meta",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    ap_election_id = models.CharField(max_length=10)
    called = models.BooleanField(default=False)
    tabulated = models.BooleanField(default=False)
    override_ap_call = models.BooleanField(default=False)
    override_ap_votes = models.BooleanField(default=False)
    precincts_reporting = models.PositiveIntegerField(null=True, blank=True)
    precincts_total = models.PositiveIntegerField(null=True, blank=True)
    precincts_reporting_pct = models.DecimalField(
        max_digits=5, decimal_places=3, null=True, blank=True
    )

    class Meta:
        verbose_name_plural = "AP election meta data"

    def __str__(self):
        return self.election.__str__()
