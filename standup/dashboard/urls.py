from django.urls import path
from dashboard import views


urlpatterns = [
path("", views.root, name="dashbord-root"),
path("get-item-detail", views.get_item_details, name="get-item-details"),   
path("solve-item", views.resolve_item, name="solve-item")
]