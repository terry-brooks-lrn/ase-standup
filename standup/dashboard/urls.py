from dashboard import views
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [

    # SECTION -  Template Rendering URLs
    path("", views.RootView.as_view(), name="home"),
    # path("support-mail", views.supportmail, name="support-mail"),
    # SECTION - AJAX Hook URLs
    path("get-item-detail", views.get_item_details, name="get-item-details"),
    path("solve-item", csrf_exempt(views.resolve_item), name="solve-item"),
    path("feat-accepted", csrf_exempt(views.mark_feat_accepted), name="mark-feat-accepted"),
    path("feat-rejected", csrf_exempt(views.mark_feat_rejected), name="mark-feat-rejected"),
    path("reopen", csrf_exempt(views.reopen_item), name="reopen-item"),
    path("convert", csrf_exempt(views.convert_to_fyi), name="move-to-monitoring"),
    path("forms/create-item", views.load_create_item_form, name="create-item-formview")
]
