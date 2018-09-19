from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .viewsets import APElectionMetaViewSet

router = DefaultRouter()
router.register(r"ap-election-meta", APElectionMetaViewSet)

urlpatterns = [path("api/", include(router.urls))]
