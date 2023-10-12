from dashboard import views
from django.urls import path

urlpatterns = [

    # SECTION -  Template Rendering URLs
    path("", views.root, name="home"),
    path("support-mail", views.supportmail, name="support-mail"),
    # SECTION - AJAX Hook URLs
    path("get-item-detail", views.get_item_details, name="get-item-details"),
    path("solve-item", views.resolve_item, name="solve-item"),
    path("feat-accepted", views.mark_feat_accepted, name="mark-feat-accepted"),
    path("feat-rejected", views.mark_feat_rejected, name="mark-feat-rejected"),
    path("reopen", views.reopen_item, name="reopen-item"),
    path("convert", views.convert_to_fyi, name="move-to-monitoring"),
]
