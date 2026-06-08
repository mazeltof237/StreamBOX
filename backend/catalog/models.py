from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Genre(models.Model):
    name = models.CharField(max_length=40, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Title(models.Model):
    KIND_MOVIE = "movie"
    KIND_SERIES = "series"
    KIND_CHOICES = [(KIND_MOVIE, "Film"), (KIND_SERIES, "Série")]
    MATURITY_CHOICES = [
        ("ALL", "Tous publics"),
        ("10", "10+"),
        ("13", "13+"),
        ("16", "16+"),
        ("18", "18+"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField(blank=True)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default=KIND_MOVIE)
    genres = models.ManyToManyField(Genre, related_name="titles", blank=True)
    year = models.PositiveIntegerField(default=2024)
    duration_minutes = models.PositiveIntegerField(default=0, help_text="Films seulement")
    maturity = models.CharField(max_length=4, choices=MATURITY_CHOICES, default="ALL")
    cast = models.CharField(max_length=400, blank=True)
    director = models.CharField(max_length=200, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    is_featured = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    poster = models.ImageField(upload_to="posters/", blank=True, null=True)
    backdrop = models.ImageField(upload_to="backdrops/", blank=True, null=True)
    poster_url = models.URLField(blank=True, help_text="Fallback si pas de fichier")
    backdrop_url = models.URLField(blank=True, help_text="Fallback si pas de fichier")
    trailer_url = models.URLField(blank=True, help_text="YouTube embed ou MP4")
    video_url = models.URLField(blank=True, help_text="MP4 source pour le lecteur")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200] or "title"
            slug = base
            i = 2
            while Title.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def poster_src(self):
        if self.poster:
            return self.poster.url
        return self.poster_url or ""

    @property
    def backdrop_src(self):
        if self.backdrop:
            return self.backdrop.url
        return self.backdrop_url or self.poster_src


class Episode(models.Model):
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name="episodes")
    season = models.PositiveIntegerField(default=1)
    number = models.PositiveIntegerField()
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    video_url = models.URLField(blank=True)
    thumbnail_url = models.URLField(blank=True)

    class Meta:
        ordering = ["season", "number"]
        unique_together = ("title", "season", "number")

    def __str__(self):
        return f"{self.title.title} S{self.season:02d}E{self.number:02d} – {self.name}"


class WatchlistItem(models.Model):
    profile = models.ForeignKey(
        "accounts.Profile", on_delete=models.CASCADE, related_name="watchlist"
    )
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name="in_watchlists")
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-added_at"]
        unique_together = ("profile", "title")


class WatchHistory(models.Model):
    profile = models.ForeignKey(
        "accounts.Profile", on_delete=models.CASCADE, related_name="history"
    )
    title = models.ForeignKey(Title, on_delete=models.CASCADE, related_name="history")
    progress_seconds = models.PositiveIntegerField(default=0)
    finished = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        unique_together = ("profile", "title")
