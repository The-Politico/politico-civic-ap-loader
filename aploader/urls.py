from django.urls import re_path, path
from rest_framework.routers import DefaultRouter

from .views import Caller
from .viewsets import APElectionMetaList

router = DefaultRouter()

urlpatterns = [
    re_path(
        "api/ap-election-meta/(?P<state>.+)/$", APElectionMetaList.as_view()
    ),
    path("calls/", Caller.as_view(), name="aploader_race-caller-admin"),
]
