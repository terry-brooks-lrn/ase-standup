from dashboard import views
from django.urls import path

urlpatterns = [
    path("", views.root, name="home"),
    path("get-item-detail", views.get_item_details, name="get-item-details"),
    path("solve-item", views.resolve_item, name="solve-item"),
    path("convert", views.convert_to_fyi, name="convert-to-visibilty"),
    path("reopen", views.reopened_item, name="reopen-item"),
    path("item-log", views.item_log, name="all-items"),
    path("supportmail", views.supportmail, name="support-mail"),
]
