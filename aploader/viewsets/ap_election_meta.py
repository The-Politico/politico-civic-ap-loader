from aploader.models import APElectionMeta
from aploader.serializers import APElectionMetaSerializer

from .base import BaseViewSet


class APElectionMetaViewSet(BaseViewSet):
    queryset = APElectionMeta.objects.all()
    serializer_class = APElectionMetaSerializer
