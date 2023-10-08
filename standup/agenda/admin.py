from agenda.models import WIN_OOPS, Agenda, Item, SupportEngineer, SupportMail
from django.contrib import admin

# Register your models here.
all_models = [Agenda, WIN_OOPS, Item, SupportEngineer, SupportMail]

for model in all_models:
    register = admin.site.register(model)
