from agenda import views
from django.urls import include, path

urlpatterns = [
    path("api-auth/", include("rest_framework.urls")),
    path("agenda/", views.AgendasViews.as_view()),
    path("agenda/<str:date>", views.AgendaView.as_view()),
    path("item/<int:id>", views.ItemViews.as_view(), name="single_item"),
    path("items/", views.ItemsViews.as_view(), name="list_of_items"),
]


handler500 = "rest_framework.exceptions.server_error"
handler400 = "rest_framework.exceptions.bad_request"
