from agenda.models import Agenda, Item, SupportEngineer, now
from agenda.seralizers import AgendaSerializer, ItemSerializer
from dashboard.forms import ItemForm
from django.db.models import Count
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from loguru import logger
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response


def root(request):
    try:
        if len(Agenda.objects.filter(date=now)) == 0:
            logger.info(f"No Agenda Created for {now} - Creating a New Agenda")
            current_agenda = Agenda(date=now)
            # current_agenda.select_driver()
        else:
            logger.warning(f"{now} Already Has Agenda Created - Skipping Creation")
            current_agenda = Agenda.objects.get(date=now)
    except IntegrityError:
        pass
    logger.debug(f"Current Agenda: {current_agenda}")
    current_agenda_json = AgendaSerializer(current_agenda)
    context = dict()
    context["item_form"] = ItemForm()
    context["open_items"] = Item.objects.filter(status__in=["NEW", "OPEN", "FYI"]).count()
    context["open_monitor_items"] = Item.objects.filter(section="MONITOR", status__in=["NEW", "OPEN", "FYI"]).order_by(
        "creator", "-date_created"
    )
    context["open_monitor_items_count"] = len(context["open_monitor_items"])
    context["open_review_items"] = Item.objects.filter(section="REVIEW", status__in=["NEW", "OPEN"]).order_by(
        "creator", "-date_created"
    )
    context["open_review_items_count"] = len(context["open_review_items"])
    context["open_calls_items"] = Item.objects.filter(section="CALLS", status__in=["NEW", "OPEN", "FYI"])
    context["open_focus_items"] = Item.objects.filter(section="FOCUS", status__in=["NEW", "OPEN", "FYI"])
    context["open_needs_items"] = Item.objects.filter(section="NEEDS", status__in=["NEW", "OPEN", "FYI"])
    context["open_updates_items"] = Item.objects.filter(section="UPDATES", status__in=["NEW", "OPEN", "FYI"])
    context["open_misc_items"] = Item.objects.filter(section="MISC", status__in=["NEW", "OPEN", "FYI"])
    context["open_internal_items"] = Item.objects.filter(section="INTERNAL", status__in=["NEW", "OPEN", "FYI"])

    context["current_agenda_date"] = current_agenda_json.data["date"]
    context["current_agenda_driver"] = SupportEngineer.objects.get(id=current_agenda_json.data["driver"]).first_name
    context["current_agenda_notetaker"] = SupportEngineer.objects.get(
        id=current_agenda_json.data["notetaker"]
    ).first_name
    return render(request, "index.html", context)


def get_item_details(request, pk):
    item = Item.objects.get(pk=pk)
    form = ItemForm(instance=item)
    return HttpResponse(request, content=form, status_code=200)


@csrf_exempt
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def resolve_item(request):
    pk = request.POST["pk"]
    item = Item.objects.get(pk=pk)
    logger.debug(f"Solving - {ItemSerializer(item)}")
    item.resolve()
    item.save()
    return HttpResponse(request, status=200)


@csrf_exempt
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def convert_to_fyi(request):
    pk = request.POST["pk"]
    item = Item.objects.get(pk=pk)
    logger.debug(f"Converting To Monitoring - {ItemSerializer(item).data}")
    item.make_visibility_only()
    item.save()
    return HttpResponse(request, status=200)
