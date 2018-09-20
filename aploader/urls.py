from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import Caller
from .viewsets import APElectionMetaViewSet

router = DefaultRouter()
router.register(r"ap-election-meta", APElectionMetaViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("calls/", Caller.as_view(), name="aploader_race-caller-admin"),
]
