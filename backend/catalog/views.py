from collections import Counter
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q, Count, Sum, Avg
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import timedelta
from functools import wraps
import json

from accounts.models import Profile, Subscription, Payment
from .models import Title, Genre, WatchlistItem, WatchHistory


def _kids_filter(qs, profile):
    if profile and profile.is_kid:
        return qs.filter(maturity__in=["ALL", "10"])
    return qs


def profile_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("accounts:login")
        # Vérifie l'abonnement (sauf staff)
        if not request.user.is_staff:
            sub = getattr(request.user, "subscription", None)
            if not sub or not sub.is_active():
                return redirect("accounts:plans")
        pid = request.session.get("active_profile_id")
        profile = Profile.objects.filter(id=pid, user=request.user).first() if pid else None
        if not profile:
            return redirect("accounts:profiles")
        request.profile = profile
        return view_func(request, *args, **kwargs)
    return _wrapped


# ---- Recommandations IA (content-based + collaboratif léger) ----
def recommend_for(profile, limit=12):
    history_qs = WatchHistory.objects.filter(profile=profile).select_related("title")
    seen_ids = set(history_qs.values_list("title_id", flat=True))
    seen_titles = [h.title for h in history_qs[:30]]

    if not seen_titles:
        # Cold-start : top notés
        qs = _kids_filter(Title.objects.all(), profile).order_by("-rating", "-is_trending")
        return list(qs[:limit])

    # 1) Content-based : score sur intersection des genres
    genre_weights = Counter()
    for t in seen_titles:
        for g in t.genres.all():
            genre_weights[g.id] += 1

    candidates = _kids_filter(
        Title.objects.exclude(id__in=seen_ids).prefetch_related("genres"),
        profile,
    )
    scored = []
    for t in candidates[:300]:
        score = sum(genre_weights.get(g.id, 0) for g in t.genres.all())
        score += float(t.rating) / 2.0
        if t.is_trending:
            score += 1.5
        scored.append((score, t))

    # 2) Boost collaboratif : titres regardés par profils ayant vu les mêmes
    similar_profiles = (
        WatchHistory.objects.filter(title_id__in=seen_ids)
        .exclude(profile=profile)
        .values_list("profile_id", flat=True)
    )
    co_views = Counter(
        WatchHistory.objects.filter(profile_id__in=similar_profiles)
        .exclude(title_id__in=seen_ids)
        .values_list("title_id", flat=True)
    )
    boosted = [(s + co_views.get(t.id, 0) * 0.8, t) for s, t in scored]
    boosted.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in boosted[:limit]]


@profile_required
def browse(request):
    qs = _kids_filter(Title.objects.all(), request.profile)

    hero = qs.filter(is_featured=True).first() or qs.first()
    trending = qs.filter(is_trending=True)[:12]
    movies = qs.filter(kind=Title.KIND_MOVIE)[:12]
    series = qs.filter(kind=Title.KIND_SERIES)[:12]

    rows_by_genre = []
    for genre in Genre.objects.all():
        items = list(qs.filter(genres=genre)[:12])
        if items:
            rows_by_genre.append((genre, items))

    history_titles = (
        Title.objects.filter(history__profile=request.profile)
        .order_by("-history__updated_at")[:12]
    )

    recommended = recommend_for(request.profile, limit=12)

    return render(request, "catalog/browse.html", {
        "hero": hero, "trending": trending, "movies": movies, "series": series,
        "rows_by_genre": rows_by_genre, "history_titles": history_titles,
        "recommended": recommended, "all_genres": Genre.objects.all(),
    })


@profile_required
def detail(request, slug):
    title = get_object_or_404(Title, slug=slug)
    if request.profile.is_kid and title.maturity not in ("ALL", "10"):
        return redirect("catalog:browse")
    in_watchlist = WatchlistItem.objects.filter(profile=request.profile, title=title).exists()
    similar = (
        Title.objects.filter(genres__in=title.genres.all())
        .exclude(pk=title.pk).distinct()[:8]
    )
    episodes_by_season = {}
    for ep in title.episodes.all():
        episodes_by_season.setdefault(ep.season, []).append(ep)

    progress = WatchHistory.objects.filter(profile=request.profile, title=title).first()
    return render(request, "catalog/detail.html", {
        "title": title, "in_watchlist": in_watchlist, "similar": similar,
        "episodes_by_season": sorted(episodes_by_season.items()),
        "progress": progress,
    })


@profile_required
def watch(request, slug):
    title = get_object_or_404(Title, slug=slug)
    if request.profile.is_kid and title.maturity not in ("ALL", "10"):
        return redirect("catalog:browse")
    history, _ = WatchHistory.objects.get_or_create(profile=request.profile, title=title)
    return render(request, "catalog/watch.html", {"title": title, "history": history})


@profile_required
@require_POST
def progress_save(request, slug):
    title = get_object_or_404(Title, slug=slug)
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        data = {}
    seconds = int(data.get("seconds", 0))
    finished = bool(data.get("finished", False))
    h, _ = WatchHistory.objects.get_or_create(profile=request.profile, title=title)
    h.progress_seconds = max(h.progress_seconds, seconds)
    if finished:
        h.finished = True
    h.save()
    return JsonResponse({"ok": True, "progress": h.progress_seconds, "finished": h.finished})


@profile_required
def search(request):
    q = request.GET.get("q", "").strip()
    results = []
    if q:
        results = _kids_filter(Title.objects.all(), request.profile).filter(
            Q(title__icontains=q) | Q(description__icontains=q)
            | Q(cast__icontains=q) | Q(director__icontains=q)
            | Q(genres__name__icontains=q)
        ).distinct()[:50]
    return render(request, "catalog/search.html", {"q": q, "results": results})


@profile_required
def my_list(request):
    items = WatchlistItem.objects.filter(profile=request.profile).select_related("title")
    return render(request, "catalog/my_list.html", {"items": items})


@profile_required
@require_POST
def toggle_watchlist(request, slug):
    title = get_object_or_404(Title, slug=slug)
    obj, created = WatchlistItem.objects.get_or_create(profile=request.profile, title=title)
    if not created:
        obj.delete()
        added = False
    else:
        added = True
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"added": added})
    return redirect("catalog:detail", slug=slug)


@profile_required
def by_genre(request, slug):
    genre = get_object_or_404(Genre, slug=slug)
    qs = _kids_filter(Title.objects.filter(genres=genre), request.profile)
    return render(request, "catalog/genre.html", {"genre": genre, "titles": qs, "all_genres": Genre.objects.all()})


# ---- Tableau de bord Admin / Reports ----
def _staff(u):
    return u.is_authenticated and u.is_staff


@user_passes_test(_staff)
def admin_dashboard(request):
    now = timezone.now()
    last_30 = now - timedelta(days=30)

    total_users = Profile.objects.values("user").distinct().count()
    total_profiles = Profile.objects.count()
    kids_profiles = Profile.objects.filter(is_kid=True).count()
    total_titles = Title.objects.count()
    total_views = WatchHistory.objects.count()
    finished_views = WatchHistory.objects.filter(finished=True).count()
    watch_minutes = WatchHistory.objects.aggregate(s=Sum("progress_seconds"))["s"] or 0
    watch_hours = round(watch_minutes / 3600, 1)

    active_subs = Subscription.objects.filter(status="active").count()
    revenue_30 = Payment.objects.filter(succeeded=True, created_at__gte=last_30).aggregate(s=Sum("amount"))["s"] or 0
    revenue_total = Payment.objects.filter(succeeded=True).aggregate(s=Sum("amount"))["s"] or 0

    top_titles = (
        Title.objects.annotate(views=Count("history"))
        .order_by("-views")[:10]
    )
    top_genres = (
        Genre.objects.annotate(views=Count("titles__history"))
        .order_by("-views")[:8]
    )
    by_plan = (
        Subscription.objects.values("plan__name")
        .annotate(c=Count("id")).order_by("-c")
    )
    avg_rating = Title.objects.aggregate(a=Avg("rating"))["a"] or 0

    # Série temporelle simplifiée (vues par jour, 14 derniers jours)
    days = []
    for i in range(13, -1, -1):
        day = (now - timedelta(days=i)).date()
        c = WatchHistory.objects.filter(updated_at__date=day).count()
        days.append({"d": day.strftime("%d/%m"), "c": c})

    return render(request, "catalog/admin_dashboard.html", {
        "kpi": {
            "users": total_users, "profiles": total_profiles, "kids": kids_profiles,
            "titles": total_titles, "views": total_views, "finished": finished_views,
            "hours": watch_hours, "active_subs": active_subs,
            "revenue_30": revenue_30, "revenue_total": revenue_total,
            "avg_rating": round(float(avg_rating), 2),
        },
        "top_titles": top_titles, "top_genres": top_genres, "by_plan": by_plan,
        "days_json": json.dumps(days),
    })
