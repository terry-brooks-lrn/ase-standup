from django.contrib import admin
from agenda.models import Agenda, WIN_OOPS, Item, SupportEngineer, SupportMail

# Register your models here.
all_models = [Agenda, WIN_OOPS, Item, SupportEngineer, SupportMail]

for model in all_models:
    register = admin.site.register(model)
