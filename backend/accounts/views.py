from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import timedelta

from .forms import SignUpForm, ProfileForm, StreamBoxLoginForm
from .models import Profile, Plan, Subscription, Payment


class StreamBoxLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = StreamBoxLoginForm
    redirect_authenticated_user = True


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:profiles")
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            Profile.objects.create(user=user, name=user.username[:40], avatar_preset="fafi")
            return redirect("accounts:plans")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("accounts:login")


@login_required
def profiles_view(request):
    profiles = request.user.profiles.all()
    if not profiles.exists():
        return redirect("accounts:profile_create")
    return render(request, "accounts/profiles.html", {"profiles": profiles})


@login_required
@require_POST
def select_profile(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id, user=request.user)
    if profile.pin:
        pin = request.POST.get("pin", "")
        if pin != profile.pin:
            messages.error(request, "Code PIN incorrect.")
            return redirect("accounts:profiles")
    request.session["active_profile_id"] = profile.id
    return redirect("catalog:browse")


@login_required
def profile_create(request):
    sub = getattr(request.user, "subscription", None)
    max_p = sub.plan.max_profiles if sub else 5
    if request.user.profiles.count() >= max_p:
        messages.error(request, f"Votre plan autorise {max_p} profils maximum.")
        return redirect("accounts:profiles")
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect("accounts:profiles")
    else:
        form = ProfileForm()
    return render(request, "accounts/profile_form.html", {"form": form, "is_create": True})


@login_required
def profile_edit(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id, user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("accounts:profiles")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "accounts/profile_form.html", {"form": form, "is_create": False, "profile": profile})


@login_required
@require_POST
def profile_delete(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id, user=request.user)
    if request.user.profiles.count() > 1:
        profile.delete()
    return redirect("accounts:profiles")


# ---- Plans / Subscription / Payments (Stripe-ready, mock par défaut) ----

@login_required
def plans_view(request):
    plans = Plan.objects.filter(is_active=True)
    current = getattr(request.user, "subscription", None)
    return render(request, "accounts/plans.html", {"plans": plans, "current": current})


@login_required
def checkout(request, code):
    plan = get_object_or_404(Plan, code=code, is_active=True)
    if request.method == "POST":
        # Simulation paiement carte (à brancher sur Stripe Checkout côté prod).
        Payment.objects.create(user=request.user, plan=plan, amount=plan.price_eur, method="card", succeeded=True)
        sub, _ = Subscription.objects.get_or_create(user=request.user, defaults={"plan": plan})
        sub.plan = plan
        sub.status = "active"
        sub.started_at = timezone.now()
        sub.renews_at = timezone.now() + timedelta(days=30)
        sub.save()
        messages.success(request, f"Abonnement {plan.name} activé !")
        return redirect("accounts:billing")
    return render(request, "accounts/checkout.html", {"plan": plan})


@login_required
def billing_view(request):
    sub = getattr(request.user, "subscription", None)
    payments = request.user.payments.all()[:20]
    return render(request, "accounts/billing.html", {"sub": sub, "payments": payments})


@login_required
@require_POST
def cancel_subscription(request):
    sub = getattr(request.user, "subscription", None)
    if sub:
        sub.status = "canceled"
        sub.save()
        messages.info(request, "Abonnement annulé. Accès jusqu'à la fin de la période.")
    return redirect("accounts:billing")
