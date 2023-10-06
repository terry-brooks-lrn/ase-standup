from agenda.models import Agenda, Item, now, WIN_OOPS, SupportEngineer
from agenda.seralizers import AgendaSerializer, ItemSerializer
from dashboard.forms import ItemForm
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from loguru import logger
from rest_framework.decorators import renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
import os
from django.conf import settings
from logtail import LogtailHandler
import pendulum

pendulum.datetime

PRIMARY_LOG_FILE = os.path.join(settings.BASE_DIR, "standup", "logs", "primary_ops.log")
CRITICAL_LOG_FILE = os.path.join(settings.BASE_DIR, "standup", "logs", "fatal.log")
DEBUG_LOG_FILE = os.path.join(settings.BASE_DIR, "standup", "logs", "utility.log")
LOGTAIL_HANDLER = LogtailHandler(source_token=os.getenv("LOGTAIL_API_KEY"))

logger.add(DEBUG_LOG_FILE, diagnose=True, catch=True, backtrace=True, level="DEBUG")
logger.add(PRIMARY_LOG_FILE, diagnose=False, catch=True, backtrace=False, level="INFO")
logger.add(LOGTAIL_HANDLER, diagnose=False, catch=True, backtrace=False, level="INFO")


# Create your views here.
def root(request):
    try:
        current_agenda = Agenda(date=now)
        current_agenda.select_driver()
        current_agenda.save()
    except IntegrityError:
        logger.warning(f"{now} Already Has Agenda Created - Skipping Creation")
    logger.debug(current_agenda)
    # current_agenda.select_driver()]
    current_agenda_json = AgendaSerializer(current_agenda)
    context = dict()
    context["item_form"] = ItemForm()
    # SECTION - Core Queries for Dashboard
    # SECTION - Count of All Open Items
    context["open_items_count"] = Item.objects.filter(
        status__in=["NEW", "OPEN", "FYI"]
    ).count()

    # SECTION - Count and Query of All Monitorimng Items
    context["open_monitor_items"] = Item.objects.filter(
        section="MONITOR", status__in=["NEW", "OPEN", "FYI"]
    ).order_by("creator", "-date_created")
    context["open_monitor_items_count"] = len(context["open_monitor_items"])

    # SECTION - Count and Query of All Review Items
    context["open_review_items"] = Item.objects.filter(
        section="REVIEW", status__in=["NEW", "OPEN"]
    ).order_by("creator", "-date_created")
    context["open_review_items_count"] = len(context["open_review_items"])

    # SECTION - Count and Query of All Client Calls Items
    context["open_calls_items"] = Item.objects.filter(
        section="CALLS", status__in=["NEW", "OPEN"]
    ).order_by("creator", "-date_created")
    context["open_call_items_count"] = len(context["open_calls_items"])

    # SECTION - Count and Query of Clients Needing Attention Items
    context["open_focus_items"] = Item.objects.filter(
        section="FOCUS", status__in=["NEW", "OPEN"]
    ).order_by("creator", "-date_created")
    context["open_focus_items_count"] = len(context["open_focus_items"])

    # SECTION - Count and Query of Team Needs  Items
    context["open_needs_items"] = Item.objects.filter(
        section="NEEDS", status__in=["NEW", "OPEN"]
    ).order_by("creator", "-date_created")
    context["open_needs_items_count"] = len(context["open_needs_items"])

    # SECTION - Count and Query of Internal Update Items
    context["open_updates_items"] = Item.objects.filter(
        section="UPDATES", status__in=["NEW", "OPEN"]
    ).order_by("creator", "-date_created")
    context["open_updates_items_count"] = len(context["open_updates_items"])

    # SECTION - Count and Query misc Items
    context["open_misc_items"] = Item.objects.filter(
        section="MISC", status__in=["NEW", "OPEN"]
    ).order_by("creator", "-date_created")
    context["open_misc_items_count"] = len(context["open_misc_items"])

    # SECTION - Count and Query Internal Items
    context["open_internal_items"] = Item.objects.filter(
        section="INTERNAL", status__in=["NEW", "OPEN"]
    ).order_by("creator", "-date_created")
    context["weeks_win_oops"] = WIN_OOPS.objects.filter(date_occured__gte=now)
    context["wins_oops_count"] = len(context["weeks_win_oops"])

    # SECTION = Stats and DRIVER Query
    context["current_agenda_date"] = current_agenda_json.data["date"]
    # context["current_agenda_driver"] = SupportEngineer.objects.get(id=current_agenda_json.data["driver"]).first_name
    context["current_agenda_notetaker"] = SupportEngineer.objects.get(
        id=current_agenda_json.data["notetaker"]
    ).first_name
    #!SECTION - Core Queries for Dashboard
    # NOTE - ROllover Function Invocation
    Agenda.statusRollOver()

    return render(request, "index.html", context)


def supportmail(request):
    context = dict()
    context["current_supportmail_topics"] = Items.objects.filter(
        added_support_mail == True
    )
    return render(request, "support_mail.html", context)


# SECTION -
def get_item_details(request, pk):
    item = Item.objects.get(pk=pk)
    form = ItemForm(instance=item)
    return HttpResponse(request, content=form, status_code=200)


@csrf_exempt
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def resolve_item(request):
    """AJAX REQUEST Hook to Resolves an item based on the PK passed in POST BOdy.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: The HTTP response object with a status code of 200.

    Raises:
        KeyError: If the 'pk' key is not found in the request's POST data.
        Item.DoesNotExist: If no item with the given primary key (pk) is found in the database.
    """

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
