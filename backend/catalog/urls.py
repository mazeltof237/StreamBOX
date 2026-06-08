from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.browse, name="browse"),
    path("search/", views.search, name="search"),
    path("my-list/", views.my_list, name="my_list"),
    path("genre/<slug:slug>/", views.by_genre, name="by_genre"),
    path("title/<slug:slug>/", views.detail, name="detail"),
    path("title/<slug:slug>/watch/", views.watch, name="watch"),
    path("title/<slug:slug>/progress/", views.progress_save, name="progress_save"),
    path("title/<slug:slug>/watchlist/", views.toggle_watchlist, name="toggle_watchlist"),
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
]
