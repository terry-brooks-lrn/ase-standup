
from agenda.models import Agenda, Item
from agenda.serializers import AgendaSerializer, ItemSerializer
from django.http import JsonResponse
from rest_framework.generics import ListCreateAPIView, CreateAPIView, DestroyAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
import os
from django.conf import settings
from logtail import LogtailHandler  
from datetime import datetime
PRIMARY_LOG_FILE = os.path.join(settings.BASE_DIR,"standup", "logs", "primary_ops.log")
CRITICAL_LOG_FILE = os.path.join(settings.BASE_DIR,"standup", "logs", "fatal.log")
DEBUG_LOG_FILE = os.path.join(settings.BASE_DIR,"standup", "logs", "utility.log")
LOGTAIL_HANDLER = LogtailHandler(source_token=os.getenv("LOGTAIL_API_KEY"))




class AgendasViews(ListCreateAPIView):
    queryset = Agenda.objects.all()
    serializer_class = AgendaSerializer


class AgendaView(RetrieveUpdateDestroyAPIView):
    queryset = Agenda.objects.all()
    serializer_class = AgendaSerializer
    lookup_field = "date"


class ModifySingleItemViews(RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = "id"


class CreateItemView(CreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

def change_driver(request):
    current_agenda = Agenda.objects.get(date=datetime.today)
    former_driver = current_agenda.driver
    current_agenda.repick_driver()
    return JsonResponse(data={"former_driver": former_driver, "new_driver": current_agenda.driver})
class DeleteItemView(DestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = "id"


class ListItemsView(ListAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer