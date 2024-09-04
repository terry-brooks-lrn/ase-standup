from supportmail.views import SupportMailView
from django.urls import path


urlpatterns = [
    path('', SupportMailView.as_view(), name="support-mail"   )
]