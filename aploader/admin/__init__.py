from django.contrib import admin

from aploader.models import APElectionMeta
from .ap_election_meta import APElectionMetaAdmin

admin.site.register(APElectionMeta, APElectionMetaAdmin)
