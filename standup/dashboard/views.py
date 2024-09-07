from django.views.generic import TemplateView
from agenda.models import WIN_OOPS, Agenda, Item, NOW, ClientCall, Update
from agenda.serializers import AgendaSerializer, ItemSerializer
from django.shortcuts import render
from dashboard.forms import ItemForm
import arrow
from loguru import logger
from django.db.utils import IntegrityError
from datetime import datetime
from rest_framework import status 
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import renderer_classes
from rest_framework.exceptions import NotFound
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

def get_filtered_items(section, statuses):
    items = Item.objects.filter(section=section, status__in=statuses).order_by("creator", "-date_created")
    return items, len(items)

class RootView(LoginRequiredMixin, TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            current_agenda = Agenda.objects.get(date=NOW)
            if  current_agenda:
                logger.warning(f"{NOW} Already Has Agenda Created - Skipping Creation")
        except ObjectDoesNotExist:
            logger.info(f'No Current Agenda for {NOW} Exists - Creating...')
            current_agenda = Agenda.objects.create(date=NOW)
            current_agenda.select_driver()

        context['item_form'] = ItemForm()

        # Query counts and lists
        context['open_items_count'] = Item.objects.filter(status__in=["NEW", "OPEN", "FYI"]).count()
        context['open_updates_items_count'] = Update.objects.filter(date_of_event__gte=NOW).count()
        context['open_updates_items'] = Update.objects.filter(date_of_event__gte=NOW)
        context['open_call_items_count'] = ClientCall.objects.filter(date_of_event__gte=NOW).count()
        context['open_call_items'] = ClientCall.objects.filter(date_of_event__gte=NOW)
        sections = ["MONITOR", "REVIEW", "FOCUS", "NEEDS", "UPDATES", "MISC", "INTERNAL"]
        for section in sections:
            items, count = get_filtered_items(section, ["NEW", "OPEN"])
            context[f'open_{section.lower()}_items'] = items
            context[f'open_{section.lower()}_items_count'] = count

        context['current_agenda_date'] = current_agenda.date
        context['current_agenda_driver'] = current_agenda.driver
        context['current_agenda_notetaker'] = current_agenda.notetaker
        context['stale_deadline'] = arrow.get(NOW).shift(days=-7).format('YYYY-MM-DD')
        last_meeting = Agenda.objects.last().date
        context['last_meeting'] = arrow.get(last_meeting).format("YYYY-MM-DD")
        if context['last_meeting'] == current_agenda.date:
            context['last_meeting'] = Agenda.objects.all().order_by("-date")[1].date

        return context

class PastAgendaView(TemplateView):
    template_name = 'past_agenda.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            desired_date = kwargs['date']
            agenda = Agenda.objects.get(date=desired_date)
            context['open_items_count'] = Item.objects.filter(date=desired_date).filter(status__in=["NEW", "OPEN", "FYI"]).count()
            context['agenda_date'] = desired_date
            context['agenda_driver'] = agenda.driver
            context['agenda_notetaker'] = agenda.notetaker
            context['open_updates_items'] = Update.objects.filter(~Q(date_created__gt=desired_date)).filter(date_of_event__gte=desired_date)
            context['open_updates_items_count'] = len(context['open_updates_items'])
            context['open_call_items'] = ClientCall.objects.filter(~Q(date_created__gt=desired_date)).filter(date_of_event__gte=desired_date)
            context['open_call_items_count'] = len(context['open_call_items'])

            sections = ["MONITOR", "REVIEW", "CALLS", "FOCUS", "NEEDS", "MISC", "INTERNAL"]
            for section in sections:
                items, count = get_filtered_items(section, ["NEW", "OPEN"])
                context[f'open_{section.lower()}_items'] = items
                context[f'open_{section.lower()}_items_count'] = count

            return context

        except ObjectDoesNotExist as NoAgenda:
            logger.warning(f"Invaild Date: {desired_date} - ERROR: {NoAgenda.date}")



# SECTION -AJAX Hook Routes
def get_item_details(request, pk):
    item = Item.objects.get(pk=pk)
    form = ItemForm(instance=item)
    return HttpResponse(content=form, status_code=status.HTTP_200_OK)

@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def resolve_item(request):
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
        ) from e
    except Exception as e:
        logger.error(f"Error When Processing AJAX Request: {e}")
        raise Exception from e

@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def convert_to_fyi(request):
    try:
        pk = request.POST["pk"]
        item = Item.objects.get(pk=pk)
        logger.debug(f"Converting To Monitoring - {ItemSerializer(item).data['title']}")
        item.make_visibility_only()
        item.save()
        return HttpResponse(request, status=status.HTTP_200_OK)
    except (KeyError, ObjectDoesNotExist) as e:
        raise NotFound(
            detail="Invalid PK passed. Unable to Convert Item to FYI",
            code=status.HTTP_404_NOT_FOUND,
        ) from e
    except Exception as e:
        logger.error(f"Error When Processing AJAX Request: {e}")
        raise Exception from e

@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def mark_feat_accepted(request):
    try:
        pk = request.POST["pk"]
        item = Item.objects.get(pk=pk)
        logger.debug(f"Marking Feature Request Accepted - {ItemSerializer(item).data}")
        item.mark_accepted()
        item.save()
        return HttpResponse(request, status=status.HTTP_200_OK)
    except (KeyError, ObjectDoesNotExist) as e:
        raise NotFound(
            detail="Invalid PK passed. Unable to Convert Item to FYI",
            code=status.HTTP_404_NOT_FOUND,
        ) from e
    except Exception as e:
        logger.error(f"Error When Processing AJAX Request: {e}")
        raise Exception from e

@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def mark_feat_rejected(request):
    try:
        pk = request.POST["pk"]
        item = Item.objects.get(pk=pk)
        logger.debug(f"Marking Feature Request Accepted - {ItemSerializer(item).data}")
        item.mark_rejected()
        item.save()
        return HttpResponse(request, status=status.HTTP_200_OK)
    except (KeyError, ObjectDoesNotExist) as e:
        raise NotFound(
            detail="Invalid PK passed. Unable to Convert Item to FYI",
            code=status.HTTP_404_NOT_FOUND,
        ) from e
    except Exception as e:
        logger.error(f"Error When Processing AJAX Request: {e}")
        raise Exception from e

@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def reopen_item(request):
    try:
        pk = request.POST["pk"]
        item = Item.objects.get(pk=pk)
        logger.debug(f"Reopening - {ItemSerializer(item).data}")
        item.reopen()
        item.save()
        return HttpResponse(request, status=status.HTTP_200_OK)
    except (KeyError, ObjectDoesNotExist) as e:
        raise NotFound(
            detail="Invalid PK passed. Unable to Convert Item to FYI",
            code=status.HTTP_404_NOT_FOUND,
        ) from e
    except Exception as e:
        logger.error(f"Error When Processing AJAX Request: {e}")
        raise Exception from e
    

def load_create_item_form(request):
    form = ItemForm()
    return render(request, '_form_template.html', {'form': form})

@renderer_classes((TemplateHTMLRenderer, JSONRenderer))
def create_new_item(request):
    try:
        pk = request.POST["pk"]
        item = Item.objects.get(pk=pk)
        logger.debug(f"Reopening - {ItemSerializer(item).data}")
        item.reopen()
        item.save()
        return HttpResponse(request, status=status.HTTP_200_OK)
    except (KeyError, ObjectDoesNotExist) as e:
        raise NotFound(
            detail="Invalid PK passed. Unable to Convert Item to FYI",
            code=status.HTTP_404_NOT_FOUND,
        ) from e
    except Exception as e:
        logger.error(f"Error When Processing AJAX Request: {e}")
        raise Exception from e
