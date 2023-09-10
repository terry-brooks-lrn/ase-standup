from django.urls import path, include
from agenda import views

urlpatterns = [
        path("api-auth/", include("rest_framework.urls")),
    path("agenda/", views.AgendaViews.as_view()),
    path("item/<int:id>", views.ItemViews.as_view(), name="single_item"),
    path("items/", views.ItemsViews.as_view(), name="list_of_items"),
]