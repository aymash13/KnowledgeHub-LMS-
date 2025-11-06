from django.urls import path
from . import views

urlpatterns = [
    path("", views.query_list, name="query_list"),
    path("new/", views.query_create, name="query_create"),
    path("<int:query_id>/", views.query_detail, name="query_detail"),
]