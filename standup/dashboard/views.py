import os

from django.conf import settings
import pendulum
from agenda.models import Agenda, Item, SupportEngineer, SupportMail, now
from agenda.seralizers import AgendaSerializer, ItemSerializer, SupportMailSerializer
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
from logtail import LogtailHandler

from standup.utility import logger_wraps

PRIMARY_LOG_FILE = os.path.join(settings.BASE_DIR, "standup", "logs", "primary_ops.log")
CRITICAL_LOG_FILE = os.path.join(settings.BASE_DIR, "standup", "logs", "fatal.log")
DEBUG_LOG_FILE = os.path.join(settings.BASE_DIR, "standup", "logs", "utility.log")
LOGTAIL_HANDLER = LogtailHandler(source_token=os.getenv("LOGTAIL_API_KEY"))
logger.add(DEBUG_LOG_FILE, diagnose=True, catch=True, backtrace=True, level="TRACE")
logger.add(PRIMARY_LOG_FILE, diagnose=False, catch=True, backtrace=False, level="INFO")
logger.add(LOGTAIL_HANDLER, diagnose=False, catch=True, backtrace=False, level="INFO")


def root(request):
    try:
        if len(Agenda.objects.filter(date=now)) == 0:
            logger.info(f"No Agenda Created for {now} - Creating a New Agenda")
            current_agenda = Agenda(date=now)
            current_agenda.select_driver()
        else:
            logger.warning(f"{now} Already Has Agenda Created - Skipping Creation")
            current_agenda = Agenda.objects.get(date=now)
    except IntegrityError:
        pass
    logger.debug(f"Current Agenda: {current_agenda}")
    current_agenda_json = AgendaSerializer(current_agenda)
    context = dict()
    # Initalizes the the form for ADD NEW ITERM MODAL
    context["item_form"] = ItemForm()
    # Database Queries to Populate the App
    # TODO: Find way to cache or optimize
    context["open_items_count"] = Item.objects.filter(
        status__in=["NEW", "OPEN"]
    ).count()
    context["open_items"] = Item.objects.filter(status__in=["NEW", "OPEN"])
    context["open_monitor_items"] = Item.objects.filter(
        section="MONITOR",
        status__in=["NEW", "OPEN", "FYI"],
    ).order_by("creator", "-date_created")
    context["open_monitor_items_count"] = len(context["open_monitor_items"])
    context["open_review_items"] = Item.objects.filter(
        section="REVIEW", status__in=["NEW", "OPEN"]
    ).order_by("creator", "-date_created")
    context["open_review_items_count"] = len(context["open_review_items"])
    context["open_calls_items"] = Item.objects.filter(
        section="CALLS", status__in=["NEW", "OPEN"]
    ).order_by("creator", "-date_created")
    context["open_calls_items_count"] = len(
        Item.objects.filter(section="CALLS", status__in=["NEW", "OPEN"]).order_by(
            "creator", "-date_created"
        )
    )

    context["open_focus_items"] = Item.objects.filter(
        section="FOCUS", status__in=["NEW", "OPEN"]
    )
    context["open_focus_items_count"] = len(context["open_focus_items"])
    context["open_needs_items"] = Item.objects.filter(
        section="NEEDS", status__in=["NEW", "OPEN"]
    )
    context["open_needs_items_count"] = len(
        Item.objects.filter(section="NEEDS", status__in=["NEW", "OPEN"])
    )
    context["open_updates_items"] = Item.objects.filter(
        section="UPDATES", status__in=["NEW", "OPEN"]
    )
    context["open_updates_items_count"] = len(context["open_updates_items"])
    context["open_misc_items"] = Item.objects.filter(
        section="MISC", status__in=["NEW", "OPEN"]
    )
    context["open_misc_items_count"] = len(context["open_misc_items"])
    context["open_internal_items"] = Item.objects.filter(
        section="INTERNAL", status__in=["NEW", "OPEN"]
    )
    context["open_internal_items_count"] = len(
        Item.objects.filter(section="INTERNAL", status__in=["NEW", "OPEN"])
    )

    context["current_agenda_date"] = current_agenda_json.data["date"]
    context["current_agenda_driver"] = SupportEngineer.objects.get(
        id=current_agenda_json.data["driver"]
    ).first_name
    context["current_agenda_notetaker"] = SupportEngineer.objects.get(
        id=current_agenda_json.data["notetaker"]
    ).first_name
    # Rolling over Items from New To Open
    # Agenda.statusRollOver()
    return render(request, "index.html", context)


def item_log(request):
    """Returns all Items thhat are in the resoolfverd status"""
    context = dict()
    context["resolved_items"] = Item.objects.filter(status="RESOLVED").order_by(
        "-date_resolved"
    )
    context["resolved_items_count`"] = len(
        Item.objects.filter(status="RESOLVED").order_by("-date_resolved")
    )
    return render(request, "item-log.html", context)


def supportmail(request):
    now = pendulum.now(tz="America/Chicago")
    current_month = now.month
    current_month = now.month
    current_year = now.year
    try:
        if (
            len(SupportMail.objects.filter(edition=current_month, year=current_year))
            == 0
        ):
            logger.info(
                f"No current support mail edition Created for {current_month} {current_year} - Creating a New Agenda"
            )
            current_edition = SupportMail(edition=current_month, year=current_year)
        else:
            logger.warning(
                f"{current_month} {current_year} Already Has Agenda Created - Skipping Creation"
            )
            current_edition = SupportMail.objects.get(
                edition=current_month, year=current_year
            )
    except IntegrityError:
        pass
    # logger.debug(f"Current SM Edition: {current_edition}")
    context = dict()
    context["current_edition"] = SupportMailSerializer(current_edition).data
    context["year"] = current_edition.year
    context["editionj"] = current_edition.edition
    context["current_supportmail_topics"] = Item.objects.filter(
        added_to_supportmail=True
    )
    return render(request, "support_mail.html", context)


def get_item_details(request, pk):
    item = Item.objects.get(pk=pk)
    form = ItemForm(instance=item)
    return HttpResponse(request, content=form, status_code=200)


@csrf_exempt
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def resolve_item(request):
    """
    Front-End Utility Endpoint targeted by Frontend AJAX Request to trigger the update of the Item Calling the endpoints status to `RESOLOVED` and update the date_resolved to the time of exeuction.
    Args:
        request (dict): The request argument typically represents the http request that is sent from the user's browser to the server to which django will be responding. It is passed implicitly at the time of execution.
    Returns:
        response (HttpResponse): An object that represents the response from the server include headers, body, status code, etc.
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
    """
    Front-End Utility Endpoint targeted by Frontend AJAX Request to trigger the update of the Item Calling the endpoints status to `MONITORING`
    Args:
        request (dict): The request argument typically represents the http request that is sent from the user's browser to the server to which django will be responding. It is passed implicitly at the time of execution.
    Returns:
        response (HttpResponse): An object that represents the response from the server include headers, body, status code, etc.
    """
    pk = request.POST["pk"]
    item = Item.objects.get(pk=pk)
    logger.debug(f"Converting To Monitoring - {ItemSerializer(item).data}")
    item.make_visibility_only()
    item.save()
    return HttpResponse(request, status=200)


@csrf_exempt
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def reopened_item(request):
    """
    Front-End Utility Endpoint targeted by Frontend AJAX Request to trigger the update of the Item Calling the endpoints status from `RESOLOVED` to 'OPEN' and set ther date_resolved value to None.
    Args:
        request (dict): The request argument typically represents the http request that is sent from the user's browser to the server to which django will be responding. It is passed implicitly at the time of execution.
    Returns:
        response (HttpResponse): An object that represents the response from the server include headers, body, status code, etc.
    """
    pk = request.POST["pk"]
    item = Item.objects.get(pk=pk)
    logger.debug(f"Reopening - {ItemSerializer(item).data}")
    item.reopen()
    item.save()
    return HttpResponse(request, status=200)
