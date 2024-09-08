from agenda import views
from django.urls import include, path

urlpatterns = [
    path("api-auth/", include("rest_framework.urls")),
    path("agenda/", views.AgendasViews.as_view()),
    path("agenda/<str:date>", views.AgendaView.as_view()),
    path("agenda/driver/reselect", views.change_driver, name="manually_select_new_driver_endpoint"),
    path("item/<int:id>", views.ModifySingleItemViews.as_view(), name="single_item_api_endpoint"),
    path("items/", views.ListItemsView.as_view(), name="list_items_api_endpoint"),
    path("item/create", views.CreateItemView.as_view(), name="create_item_api_endpoint"),
    path("item/<int:id>/delete", views.DeleteItemView.as_view(), name="delete_item_api_endpoint"),
]

handler500 = "rest_framework.exceptions.server_error"
handler400 = "rest_framework.exceptions.bad_request"
