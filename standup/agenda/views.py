
from agenda.models import Agenda, Item
from agenda.seralizers import AgendaSerializer, ItemSerializer
from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

PRIMARY_LOG_FILE = os.path.join(settings.BASE_DIR,"standup", "logs", "primary_ops.log")
CRITICAL_LOG_FILE = os.path.join(settings.BASE_DIR,"standup", "logs", "fatal.log")
DEBUG_LOG_FILE = os.path.join(settings.BASE_DIR,"standup", "logs", "utility.log")
LOGTAIL_HANDLER = LogtailHandler(source_token=os.getenv("LOGTAIL_API_KEY"))

def index(request):
    context = dict()
    return render(request, "index.html", context)


def create_new_item(request):
    pass


class AgendasViews(ListCreateAPIView):
    queryset = Agenda.objects.all()
    serializer_class = AgendaSerializer


class AgendaView(RetrieveUpdateDestroyAPIView):
    queryset = Agenda.objects.all()
    serializer_class = AgendaSerializer
    lookup_field = "date"


class ItemViews(RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = "id"


class ItemsViews(ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
