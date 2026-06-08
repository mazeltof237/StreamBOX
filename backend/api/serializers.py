from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from accounts.models import Profile, Plan, Subscription, Payment
from catalog.models import Title, Genre, Episode, WatchlistItem, WatchHistory

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "is_staff")


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user, name=user.username[:40], avatar_preset="fafi")
        return user


class ProfileSerializer(serializers.ModelSerializer):
    has_pin = serializers.SerializerMethodField()
    initial = serializers.CharField(read_only=True)

    class Meta:
        model = Profile
        fields = ("id", "name", "avatar_preset", "is_kid", "has_pin", "initial", "created_at")
        read_only_fields = ("id", "created_at", "initial")

    def get_has_pin(self, obj):
        return bool(obj.pin)


class ProfileWriteSerializer(serializers.ModelSerializer):
    pin = serializers.CharField(required=False, allow_blank=True, max_length=4)

    class Meta:
        model = Profile
        fields = ("id", "name", "avatar_preset", "is_kid", "pin")


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name", "slug")


class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode
        fields = ("id", "season", "number", "name", "description",
                  "duration_minutes", "video_url", "thumbnail_url")


class TitleListSerializer(serializers.ModelSerializer):
    poster = serializers.CharField(source="poster_src", read_only=True)
    backdrop = serializers.CharField(source="backdrop_src", read_only=True)
    kind_display = serializers.CharField(source="get_kind_display", read_only=True)

    class Meta:
        model = Title
        fields = ("id", "slug", "title", "year", "kind", "kind_display",
                  "maturity", "rating", "poster", "backdrop", "is_featured", "is_trending")


class TitleDetailSerializer(TitleListSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    episodes = EpisodeSerializer(many=True, read_only=True)

    class Meta(TitleListSerializer.Meta):
        fields = TitleListSerializer.Meta.fields + (
            "description", "duration_minutes", "cast", "director",
            "video_url", "trailer_url", "genres", "episodes",
        )


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ("id", "code", "name", "price_eur", "quality",
                  "max_profiles", "simultaneous_streams", "description", "is_active")


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    active = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ("plan", "status", "started_at", "renews_at", "active")

    def get_active(self, obj):
        return obj.is_active()


class PaymentSerializer(serializers.ModelSerializer):
    plan = serializers.CharField(source="plan.name", read_only=True)

    class Meta:
        model = Payment
        fields = ("id", "plan", "amount", "method", "succeeded", "created_at")


class WatchHistorySerializer(serializers.ModelSerializer):
    title = TitleListSerializer(read_only=True)

    class Meta:
        model = WatchHistory
        fields = ("title", "progress_seconds", "finished", "updated_at")


class WatchlistSerializer(serializers.ModelSerializer):
    title = TitleListSerializer(read_only=True)

    class Meta:
        model = WatchlistItem
        fields = ("title", "added_at")
