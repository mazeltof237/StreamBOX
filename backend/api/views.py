from collections import Counter
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Sum, Avg
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status, viewsets, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Profile, Plan, Subscription, Payment
from catalog.models import Title, Genre, WatchlistItem, WatchHistory

from . import serializers as S

User = get_user_model()


def _tokens(user):
    refresh = RefreshToken.for_user(user)
    return {"access": str(refresh.access_token), "refresh": str(refresh)}


# ---------- AUTH ----------
class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        ser = S.SignUpSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        return Response({"user": S.UserSerializer(user).data, **_tokens(user)},
                        status=status.HTTP_201_CREATED)


class MeView(APIView):
    def get(self, request):
        sub = getattr(request.user, "subscription", None)
        return Response({
            "user": S.UserSerializer(request.user).data,
            "subscription": S.SubscriptionSerializer(sub).data if sub else None,
        })


# ---------- PROFILES ----------
def _resolve_profile(request):
    pid = request.headers.get("X-Profile-Id") or request.query_params.get("profile")
    if not pid:
        return None
    return Profile.objects.filter(id=pid, user=request.user).first()


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = S.ProfileSerializer

    def get_queryset(self):
        return Profile.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return S.ProfileWriteSerializer
        return S.ProfileSerializer

    def perform_create(self, serializer):
        sub = getattr(self.request.user, "subscription", None)
        max_p = sub.plan.max_profiles if sub else 5
        if self.request.user.profiles.count() >= max_p:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(f"Limite de {max_p} profils atteinte pour votre plan.")
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def verify_pin(self, request, pk=None):
        profile = self.get_object()
        pin = request.data.get("pin", "")
        if profile.pin and pin != profile.pin:
            return Response({"ok": False, "error": "PIN incorrect"}, status=403)
        return Response({"ok": True, "profile": S.ProfileSerializer(profile).data})


# ---------- CATALOG ----------
def _kids_filter(qs, profile):
    if profile and profile.is_kid:
        return qs.filter(maturity__in=["ALL", "10"])
    return qs


def recommend_for(profile, limit=12):
    history_qs = WatchHistory.objects.filter(profile=profile).select_related("title")
    seen_ids = set(history_qs.values_list("title_id", flat=True))
    seen_titles = [h.title for h in history_qs[:30]]
    if not seen_titles:
        return list(_kids_filter(Title.objects.all(), profile).order_by("-rating", "-is_trending")[:limit])
    genre_weights = Counter()
    for t in seen_titles:
        for g in t.genres.all():
            genre_weights[g.id] += 1
    candidates = _kids_filter(Title.objects.exclude(id__in=seen_ids).prefetch_related("genres"), profile)
    scored = []
    for t in candidates[:300]:
        score = sum(genre_weights.get(g.id, 0) for g in t.genres.all())
        score += float(t.rating) / 2.0
        if t.is_trending:
            score += 1.5
        scored.append((score, t))
    similar_profiles = (WatchHistory.objects.filter(title_id__in=seen_ids)
                        .exclude(profile=profile).values_list("profile_id", flat=True))
    co_views = Counter(WatchHistory.objects.filter(profile_id__in=similar_profiles)
                       .exclude(title_id__in=seen_ids).values_list("title_id", flat=True))
    boosted = [(s + co_views.get(t.id, 0) * 0.8, t) for s, t in scored]
    boosted.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in boosted[:limit]]


class BrowseView(APIView):
    def get(self, request):
        profile = _resolve_profile(request)
        qs = _kids_filter(Title.objects.all(), profile)
        L = S.TitleListSerializer
        hero_obj = qs.filter(is_featured=True).first() or qs.first()
        history_titles = []
        recommended = []
        if profile:
            history_titles = list(Title.objects.filter(history__profile=profile)
                                  .order_by("-history__updated_at")[:12])
            recommended = recommend_for(profile, limit=12)
        rows = []
        for g in Genre.objects.all():
            items = list(qs.filter(genres=g)[:12])
            if items:
                rows.append({"genre": S.GenreSerializer(g).data, "items": L(items, many=True).data})
        return Response({
            "hero": S.TitleDetailSerializer(hero_obj).data if hero_obj else None,
            "trending": L(qs.filter(is_trending=True)[:12], many=True).data,
            "movies": L(qs.filter(kind="movie")[:12], many=True).data,
            "series": L(qs.filter(kind="series")[:12], many=True).data,
            "history": L(history_titles, many=True).data,
            "recommended": L(recommended, many=True).data,
            "rows_by_genre": rows,
            "genres": S.GenreSerializer(Genre.objects.all(), many=True).data,
        })


class TitleViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    lookup_field = "slug"
    queryset = Title.objects.all()

    def get_serializer_class(self):
        return S.TitleDetailSerializer if self.action == "retrieve" else S.TitleListSerializer

    def get_queryset(self):
        profile = _resolve_profile(self.request)
        qs = _kids_filter(Title.objects.all(), profile)
        genre = self.request.query_params.get("genre")
        q = self.request.query_params.get("q")
        if genre:
            qs = qs.filter(genres__slug=genre)
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q)
                           | Q(cast__icontains=q) | Q(director__icontains=q)
                           | Q(genres__name__icontains=q)).distinct()
        return qs

    @action(detail=True, methods=["get"])
    def similar(self, request, slug=None):
        title = self.get_object()
        items = (Title.objects.filter(genres__in=title.genres.all())
                 .exclude(pk=title.pk).distinct()[:8])
        return Response(S.TitleListSerializer(items, many=True).data)

    @action(detail=True, methods=["post"])
    def progress(self, request, slug=None):
        profile = _resolve_profile(request)
        if not profile:
            return Response({"error": "profile required"}, status=400)
        title = self.get_object()
        seconds = int(request.data.get("seconds", 0))
        finished = bool(request.data.get("finished", False))
        h, _ = WatchHistory.objects.get_or_create(profile=profile, title=title)
        h.progress_seconds = max(h.progress_seconds, seconds)
        if finished:
            h.finished = True
        h.save()
        return Response({"ok": True, "progress": h.progress_seconds, "finished": h.finished})

    @action(detail=True, methods=["post"])
    def watchlist(self, request, slug=None):
        profile = _resolve_profile(request)
        if not profile:
            return Response({"error": "profile required"}, status=400)
        title = self.get_object()
        obj, created = WatchlistItem.objects.get_or_create(profile=profile, title=title)
        if not created:
            obj.delete()
            return Response({"added": False})
        return Response({"added": True})


class GenreViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Genre.objects.all()
    serializer_class = S.GenreSerializer


class WatchlistView(APIView):
    def get(self, request):
        profile = _resolve_profile(request)
        if not profile:
            return Response([])
        items = WatchlistItem.objects.filter(profile=profile).select_related("title")
        return Response(S.WatchlistSerializer(items, many=True).data)


class HistoryView(APIView):
    def get(self, request):
        profile = _resolve_profile(request)
        if not profile:
            return Response([])
        items = WatchHistory.objects.filter(profile=profile).select_related("title")[:30]
        return Response(S.WatchHistorySerializer(items, many=True).data)


# ---------- PLANS / SUBSCRIPTION / PAYMENTS ----------
class PlanViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Plan.objects.filter(is_active=True)
    serializer_class = S.PlanSerializer
    permission_classes = [AllowAny]


class SubscribeView(APIView):
    def post(self, request):
        code = request.data.get("plan_code")
        plan = get_object_or_404(Plan, code=code, is_active=True)
        Payment.objects.create(user=request.user, plan=plan, amount=plan.price_eur,
                               method="card", succeeded=True)
        sub, _ = Subscription.objects.get_or_create(user=request.user, defaults={"plan": plan})
        sub.plan = plan
        sub.status = "active"
        sub.started_at = timezone.now()
        sub.renews_at = timezone.now() + timedelta(days=30)
        sub.save()
        return Response({"ok": True, "subscription": S.SubscriptionSerializer(sub).data})


class CancelSubscriptionView(APIView):
    def post(self, request):
        sub = getattr(request.user, "subscription", None)
        if sub:
            sub.status = "canceled"
            sub.save()
        return Response({"ok": True})


class BillingView(APIView):
    def get(self, request):
        sub = getattr(request.user, "subscription", None)
        payments = request.user.payments.all()[:20]
        return Response({
            "subscription": S.SubscriptionSerializer(sub).data if sub else None,
            "payments": S.PaymentSerializer(payments, many=True).data,
        })


# ---------- ADMIN DASHBOARD ----------
class AdminDashboardView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        now = timezone.now()
        last_30 = now - timedelta(days=30)
        watch_seconds = WatchHistory.objects.aggregate(s=Sum("progress_seconds"))["s"] or 0
        kpi = {
            "users": Profile.objects.values("user").distinct().count(),
            "profiles": Profile.objects.count(),
            "kids": Profile.objects.filter(is_kid=True).count(),
            "titles": Title.objects.count(),
            "views": WatchHistory.objects.count(),
            "finished": WatchHistory.objects.filter(finished=True).count(),
            "hours": round(watch_seconds / 3600, 1),
            "active_subs": Subscription.objects.filter(status="active").count(),
            "revenue_30": float(Payment.objects.filter(succeeded=True, created_at__gte=last_30)
                                .aggregate(s=Sum("amount"))["s"] or 0),
            "revenue_total": float(Payment.objects.filter(succeeded=True)
                                   .aggregate(s=Sum("amount"))["s"] or 0),
            "avg_rating": round(float(Title.objects.aggregate(a=Avg("rating"))["a"] or 0), 2),
        }
        top_titles = [{"title": t.title, "views": t.views}
                      for t in Title.objects.annotate(views=Count("history")).order_by("-views")[:10]]
        top_genres = [{"name": g.name, "views": g.views}
                      for g in Genre.objects.annotate(views=Count("titles__history")).order_by("-views")[:8]]
        by_plan = list(Subscription.objects.values("plan__name").annotate(c=Count("id")).order_by("-c"))
        days = []
        for i in range(13, -1, -1):
            day = (now - timedelta(days=i)).date()
            days.append({"d": day.strftime("%d/%m"),
                         "c": WatchHistory.objects.filter(updated_at__date=day).count()})
        return Response({"kpi": kpi, "top_titles": top_titles, "top_genres": top_genres,
                         "by_plan": by_plan, "days": days})
