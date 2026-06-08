from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.StreamBoxLoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("signup/", views.signup_view, name="signup"),
    path("profiles/", views.profiles_view, name="profiles"),
    path("profiles/select/<int:profile_id>/", views.select_profile, name="select_profile"),
    path("profiles/new/", views.profile_create, name="profile_create"),
    path("profiles/<int:profile_id>/edit/", views.profile_edit, name="profile_edit"),
    path("profiles/<int:profile_id>/delete/", views.profile_delete, name="profile_delete"),
    path("plans/", views.plans_view, name="plans"),
    path("checkout/<slug:code>/", views.checkout, name="checkout"),
    path("billing/", views.billing_view, name="billing"),
    path("billing/cancel/", views.cancel_subscription, name="cancel_subscription"),
]
