from django.shortcuts import render
from agenda.models import Agenda, Item, WIN_OOPS, SupportMail
from rest_framework.response import Response
from rest_framework.filters import SearchFilter
from rest_framework.generics import (
    GenericAPIView,
    ListAPIView,
    RetrieveAPIView,
    RetrieveDestroyAPIView,
    RetrieveUpdateDestroyAPIView,
    ListCreateAPIView,
)
from django.http import JsonResponse, request
from agenda.seralizers import AgendaSerializer, ItemSerializer


def index(request):
    context = dict()
    return render(request, "index.html", context)


def create_new_item(request):
    pass


class AgendaViews(ListCreateAPIView):
    queryset = Agenda.objects.all()
    serializer_class = AgendaSerializer


class ItemViews(RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = "id"


class ItemsViews(ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
