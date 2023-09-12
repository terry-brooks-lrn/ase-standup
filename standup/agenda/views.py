from agenda.models import WIN_OOPS, Agenda, Item, SupportMail
from agenda.seralizers import AgendaSerializer, ItemSerializer
from django.http import JsonResponse, request
from django.shortcuts import render
from rest_framework.filters import SearchFilter
from rest_framework.generics import (
    GenericAPIView, ListAPIView, ListCreateAPIView, RetrieveAPIView, RetrieveDestroyAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.response import Response


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
