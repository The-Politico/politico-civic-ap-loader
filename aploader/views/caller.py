from aploader.conf import settings as app_settings
from aploader.utils.auth import secure
from django.views.generic import TemplateView


@secure
class Caller(TemplateView):
    template_name = "aploader/caller.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["secret"] = app_settings.SECRET_KEY
        return context
