from django.shortcuts import render
from agenda.models import Agenda, Item
from rest_framework.generics import (
    RetrieveUpdateDestroyAPIView,
    ListCreateAPIView,
)
from agenda.seralizers import AgendaSerializer, ItemSerializer


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
