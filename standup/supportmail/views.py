from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


# Create your views here.


class SupportMailView(LoginRequiredMixin,TemplateView):
    template_name = "support_mail.html"

    