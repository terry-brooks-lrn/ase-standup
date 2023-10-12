import os


import pendulum
from agenda.models import WIN_OOPS, Agenda, Item, SupportEngineer, NOW
from agenda.seralizers import AgendaSerializer, ItemSerializer
from dashboard.forms import ItemForm
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from logtail import LogtailHandler
from loguru import logger
from rest_framework.decorators import renderer_classes
from rest_framework.exceptions import NotFound
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework import status
from django.contrib.auth import authenticate, login


PRIMARY_LOG_FILE = os.path.join(settings.BASE_DIR, "standup", "logs", "primary_ops.log")
CRITICAL_LOG_FILE = os.path.join(settings.BASE_DIR, "standup", "logs", "fatal.log")
DEBUG_LOG_FILE = os.path.join(settings.BASE_DIR, "standup", "logs", "utility.log")
LOGTAIL_HANDLER = LogtailHandler(source_token=os.getenv("LOGTAIL_API_KEY"))

logger.add(DEBUG_LOG_FILE, diagnose=True, catch=True, backtrace=True, level="DEBUG")
logger.add(PRIMARY_LOG_FILE, diagnose=False, catch=True, backtrace=False, level="INFO")
logger.add(LOGTAIL_HANDLER, diagnose=False, catch=True, backtrace=False, level="INFO")


# SECTION -  Template-Rendering Routes
def root(request):
    try:
        current_agenda = Agenda(date=NOW)
        current_agenda.select_driver()
        current_agenda.save()
    except IntegrityError:
        logger.warning(f"{NOW} Already Has Agenda Created - Skipping Creation")
    # current_agenda.select_driver()]
    current_agenda_json = AgendaSerializer(current_agenda)
    context = dict()
    context["item_form"] = ItemForm()
    # SECTION - Core Queries for Dashboard
    # SECTION - Count of All Open Items
    context["open_items_count"] = Item.objects.filter(
        status__in=["NEW", "OPEN", "FYI"]
    ).count()
    #!SECTION

    # SECTION - Count and Query of All Monitorimng Items
    context["open_monitor_items"] = Item.objects.filter(
        section="MONITOR", status__in=["NEW", "OPEN", "FYI"]
    ).order_by("creator", "-date_created")
    context["open_monitor_items_count"] = len(context["open_monitor_items"])
    #!SECTION

    # SECTION - Count and Query of All Review Items
    context["open_review_items"] = Item.objects.filter(
        section="REVIEW", status__in=["NEW", "OPEN"]
    ).order_by("creator", "-date_created")
    context["open_review_items_count"] = len(context["open_review_items"])
    #!SECTION

    # SECTION - Count and Query of All Client Calls Items
    context["open_calls_items"] = Item.objects.filter(
        section="CALLS", status__in=["NEW", "OPEN"]
    ).order_by("creator", "-date_created")
    context["open_call_items_count"] = len(context["open_calls_items"])
    #!SECTION

    # SECTION - Count and Query of Clients Needing Attention Items
    context["open_focus_items"] = Item.objects.filter(
        section="FOCUS", status__in=["NEW", "OPEN"]
    ).order_by("creator", "-date_created")
    context["open_focus_items_count"] = len(context["open_focus_items"])
    #!SECTION

    # SECTION - Count and Query of Team Needs  Items
    context["open_needs_items"] = Item.objects.filter(
        section="NEEDS", status__in=["NEW", "OPEN"]
    ).order_by("creator", "-date_created")
    context["open_needs_items_count"] = len(context["open_needs_items"])
    #!SECTION

    # SECTION - Count and Query of Internal Update Items
    context["open_updates_items"] = Item.objects.filter(
        section="UPDATES", status__in=["NEW", "OPEN"]
    ).order_by("creator", "-date_created")
    context["open_updates_items_count"] = len(context["open_updates_items"])
    #!SECTION

    # SECTION - Count and Query misc Items
    context["open_misc_items"] = Item.objects.filter(
        section="MISC", status__in=["NEW", "OPEN"]
    ).order_by("creator", "-date_created")
    context["open_misc_items_count"] = len(context["open_misc_items"])
    #!SECTION

    # SECTION - Count and Query Internal Items
    context["open_internal_items"] = Item.objects.filter(
        section="INTERNAL", status__in=["NEW", "OPEN"]
    ).order_by("creator", "-date_created")
    context["weeks_win_oops"] = WIN_OOPS.objects.filter(date_occured__gte=NOW)
    context["wins_oops_count"] = len(context["weeks_win_oops"])
    #! SECTION -
    # SECTION = Stats and DRIVER Query
    context["current_agenda_date"] = current_agenda_json.data["date"]
    context["current_agenda_driver"] = current_agenda.driver
    context["current_agenda_notetaker"] = current_agenda.notetaker
    context["stale_deadline"] = pendulum.datetime(
        month=int(NOW.split("-")[1]),
        day=int(NOW.split("-")[2]),
        year=int(NOW.split("-")[0]),
    ).add(days=7)
    context["last_meeting"] = Agenda.objects.last().date
    context["last_meeting"] = pendulum.datetime(
        month=int(context["last_meeting"].split("-")[1]),
        day=int(context["last_meeting"].split("-")[2]),
        year=int(context["last_meeting"].split("-")[0]),
    )
    if context["last_meeting"] == current_agenda:
        context["last_meeting"] = Agenda.objects.all().order_by("-date")[1].date
    logger.debug(type(context["last_meeting"]))
    #!SECTION - Core Queries for Dashboard
    # NOTE - ROllover Function Invocation
    # Agenda.statusRollOver()

    return render(request, "index.html", context)


def supportmail(request):
    context = dict()
    context["current_supportmail_topics"] = Items.objects.filter(
        added_support_mail == True
    )


#!SECTION - Template-Rendering Routes


# SECTION -AJAX Hook Routes
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
        HttpResponse (Status Code: 200): The HTTP response object with a status code of 200.

    Raises:
        NotFound (Status Code: 404): If no item with the given primary key (pk) is found in the database.
        Exception (Status Code: )
    """

    pk = request.POST["pk"]
    try:
        item = Item.objects.get(pk=pk)
        logger.debug(f"Solving - {ItemSerializer(item)}")
        item.resolve()
        item.save()
        return HttpResponse(request, status=status.HTTP_200_OK)
    except (KeyError, ObjectDoesNotExist) as e:
        logger.debug(f"FAILED attempt to resolve an Item: {e}")
        raise NotFound(
            detail="Invalid PK passed. Unable to Resolve Item",
            code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        logger.error(f"Error When Processing AJAX Request: {e}")
        raise Exception


@csrf_exempt
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def convert_to_fyi(request):
    """AJAX REQUEST Hook to convert an item to Monitoring Status.

    This JS Request endpoint updates2 the following fields of based on the PK passed in POST BOdy.:
    * Item.section to 'MONITOR'
    * Item.status tO 'FYI'

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse (Status Code: 200): The HTTP response object with a status code of 200.

    Raises:
        NotFound (Status Code: 404): If no item with the given primary key (pk) is found in the database.
    """
    try:
        pk = request.POST["pk"]
        item = Item.objects.get(pk=pk)
        logger.debug(f"Converting To Monitoring - {ItemSerializer(item).data['title']}")
        item.make_visibility_only()
        item.save()
        return HttpResponse(request, status=status.HTTP_200_OK)
    except (KeyError, DoesNotExist) as e:
        raise NotFound(
            detail="Invalid PK passed. Unable to Convert Item to FYI",
            code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        logger.error(f"Error When Processing AJAX Request: {e}")
        raise Exception


@csrf_exempt
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def mark_feat_accepted(request):
    """AJAX REQUEST Hook to convert an IFEAT item to status to 'ACCEPTED'.

    This JS Request endpoint updates the following fields of based on the PK passed in POST BOdy.:
    * Item.status tO 'ACCEPTED'

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse (Status Code: 200): The HTTP response object with a status code of 200.

    Raises:
        NotFound (Status Code: 404): If no item with the given primary key (pk) is found in the database.
    """
    try:
        pk = request.POST["pk"]
        item = Item.objects.get(pk=pk)
        logger.debug(f"Marking Feature Request Accepted - {ItemSerializer(item).data}")
        item.mark_accepted()
        item.save()
        return HttpResponse(request, status=status.HTTP_200_OK)
    except (KeyError, DoesNotExist) as e:
        raise NotFound(
            detail="Invalid PK passed. Unable to Convert Item to FYI",
            code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        logger.error(f"Error When Processing AJAX Request: {e}")
        raise Exception


@csrf_exempt
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def mark_feat_rejected(request):
    """AJAX REQUEST Hook to convert an IFEAT item to status to 'REJECTED'.

    This JS Request endpoint updates the following fields of based on the PK passed in POST BOdy.:
    * Item.status tO 'REJECTED'

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse (Status Code: 200): The HTTP response object with a status code of 200.

    Raises:
        NotFound (Status Code: 404): If no item with the given primary key (pk) is found in the database.
    """
    try:
        pk = request.POST["pk"]
        item = Item.objects.get(pk=pk)
        logger.debug(f"Marking Feature Request Accepted - {ItemSerializer(item).data}")
        item.mark_rejected()
        item.save()
        return HttpResponse(request, status=status.HTTP_200_OK)
    except (KeyError, DoesNotExist) as e:
        raise NotFound(
            detail="Invalid PK passed. Unable to Convert Item to FYI",
            code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        logger.error(f"Error When Processing AJAX Request: {e}")
        raise Exception


@csrf_exempt
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def reopen_item(request):
    """AJAX REQUEST Hook to update status re-open an item in a terminal status (i.e. RESOLVED, PUbLISHED, ACCEPTED, REJECTED)

    This JS Request endpoint updates the following fields of based on the PK passed in POST BOdy.:
    * Item.status tO 'OPEN' not an Monitoring only secton

    * If Item.section is 'FYI', the status is changed to "FYI"

    * In both situations, the `date_resolved` is changed to 'None'

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse (Status Code: 200): The HTTP response object with a status code of 200.

    Raises:
        NotFound (Status Code: 404): If no item with the given primary key (pk) is found in the database.
    """
    try:
        pk = request.POST["pk"]
        item = Item.objects.get(pk=pk)
        logger.debug(f"Reopening - {ItemSerializer(item).data}")
        item.reopen()
        item.save()
        return HttpResponse(request, status=status.HTTP_200_OK)
    except (KeyError, DoesNotExist) as e:
        raise NotFound(
            detail="Invalid PK passed. Unable to Convert Item to FYI",
            code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        logger.error(f"Error When Processing AJAX Request: {e}")
        raise Exception


@csrf_exempt
@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def create_new_item(request):
    """AJAX REQUEST Hook to create a new agenda item

    This JS Request endpoint seriaslizes the body of the post, which as been designed to match the shape of the Items model, and hits the REST API endpoint of tjje

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse (Status Code: 200): The HTTP response object with a status code of 200.

    Raises:
        NotFound (Status Code: 404): If no item with the given primary key (pk) is found in the database.
    """
    try:
        pk = request.POST["pk"]
        item = Item.objects.get(pk=pk)
        logger.debug(f"Reopening - {ItemSerializer(item).data}")
        item.reopen()
        item.save()
        return HttpResponse(request, status=status.HTTP_200_OK)
    except (KeyError, DoesNotExist) as e:
        raise NotFound(
            detail="Invalid PK passed. Unable to Convert Item to FYI",
            code=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        logger.error(f"Error When Processing AJAX Request: {e}")
        raise Exception


#!SECTION
