from django.urls import path
from dashboard import views


urlpatterns = [
    path("", views.root, name="home"),
    path("get-item-detail", views.get_item_details, name="get-item-details"),
    path("solve-item", views.resolve_item, name="solve-item"),
    path("support-mail", views.supportmail, name="support-mail"),
]
