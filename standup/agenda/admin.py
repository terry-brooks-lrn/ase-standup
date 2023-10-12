from agenda.models import WIN_OOPS, Agenda, Item, SupportEngineer, SupportMail
from django.contrib import admin
from django.db import models

from martor.widgets import AdminMartorWidget


class ItemsModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {"widget": AdminMartorWidget},
    }


class WIN_OOPSModelAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {"widget": AdminMartorWidget},
    }


# Register your models here.
all_models = [Agenda, SupportEngineer, SupportMail]


admin.site.register(Item, ItemsModelAdmin)
admin.site.register(WIN_OOPS, WIN_OOPSModelAdmin)


for model in all_models:
    register = admin.site.register(model)
