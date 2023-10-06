from dashboard import views
from django.urls import path

urlpatterns = [
    path("", views.root, name="dashbord-root"),
    path("get-item-detail", views.get_item_details, name="get-item-details"),
    path("solve-item", views.resolve_item, name="solve-item"),
    path("convert", views.convert_to_fyi, name="convert-to-visibilty"),
]
