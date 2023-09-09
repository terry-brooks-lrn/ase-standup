from django.shortcuts import render
from dashboard.forms import ItemForm
from agenda.models import Item, Agenda, now, SupportEngineer
from loguru import logger
from agenda.seralizers import AgendaSerializer
from django.db.utils import IntegrityError
# Create your views here.
def root(request):
    try:
        current_agenda = Agenda(date=now)
        current_agenda.select_driver()
        current_agenda.save()
    except IntegrityError:
        logger.warning(f"{now} Already Has Agenda Created - Skipping Creation")
    logger.debug(dir(current_agenda))
    # current_agenda.select_driver()]
    current_agenda_json = AgendaSerializer(current_agenda)
    context = dict()
    context['item_form'] = ItemForm()
    context['open_items'] = Item.objects.filter(status__in=["NEW", "OPEN", "FYI"]).count()
    context['']
    context['current_agenda_date'] = current_agenda_json.data['date']
    context['current_agenda_driver'] = SupportEngineer.objects.get(id=current_agenda_json.data['driver']).first_name
    context['current_agenda_notetaker'] = SupportEngineer.objects.get(id=current_agenda_json.data['notetaker']).first_name
    return render(request, "index.html", context)