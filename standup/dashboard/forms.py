from django.forms import ModelForm
from agenda.models import Agenda, Item, WIN_OOPS
class ItemForm(ModelForm):
    class Meta:
        model = Item
        fields = "__all__"