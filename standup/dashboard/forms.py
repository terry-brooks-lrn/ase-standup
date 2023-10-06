from agenda.models import WIN_OOPS, Agenda, Item
from django.forms import ModelForm


class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = (
            "creator",
            "section",
            "title",
            "link_to_ticket",
            "description",
            "notes",
        )
