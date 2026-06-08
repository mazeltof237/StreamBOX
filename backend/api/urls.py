from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

router = DefaultRouter()
router.register("profiles", views.ProfileViewSet, basename="profile")
router.register("titles", views.TitleViewSet, basename="title")
router.register("genres", views.GenreViewSet, basename="genre")
router.register("plans", views.PlanViewSet, basename="plan")

urlpatterns = [
    path("auth/login/", TokenObtainPairView.as_view(), name="api_login"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="api_refresh"),
    path("auth/signup/", views.SignUpView.as_view(), name="api_signup"),
    path("auth/me/", views.MeView.as_view(), name="api_me"),

    path("browse/", views.BrowseView.as_view()),
    path("watchlist/", views.WatchlistView.as_view()),
    path("history/", views.HistoryView.as_view()),

    path("subscribe/", views.SubscribeView.as_view()),
    path("subscription/cancel/", views.CancelSubscriptionView.as_view()),
    path("billing/", views.BillingView.as_view()),

    path("admin/dashboard/", views.AdminDashboardView.as_view()),

    path("", include(router.urls)),
]
