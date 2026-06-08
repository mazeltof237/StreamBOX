"""Admin Django StreamBOX — interface personnalisée (bonus)."""
from django.contrib import admin
from django.utils.html import format_html
from .models import Genre, Title, Episode, WatchlistItem, WatchHistory


admin.site.site_header = "🎬 StreamBOX Administration"
admin.site.site_title = "StreamBOX Admin"
admin.site.index_title = "Tableau de bord — gestion du catalogue & des abonnés"


class EpisodeInline(admin.TabularInline):
    model = Episode
    extra = 1
    fields = ("season", "number", "name", "duration_minutes", "video_url")


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ("poster_thumb", "title", "kind", "year", "maturity",
                    "rating", "is_featured", "is_trending", "genres_list")
    list_display_links = ("poster_thumb", "title")
    list_filter = ("kind", "is_featured", "is_trending", "maturity", "genres", "year")
    search_fields = ("title", "cast", "director", "description")
    filter_horizontal = ("genres",)
    prepopulated_fields = {"slug": ("title",)}
    list_per_page = 25
    list_editable = ("is_featured", "is_trending")
    inlines = [EpisodeInline]
    actions = ["mark_featured", "unmark_featured", "mark_trending", "unmark_trending"]
    fieldsets = (
        ("Informations principales", {
            "fields": ("title", "slug", "kind", "description", "genres")
        }),
        ("Détails", {
            "fields": ("year", "duration_minutes", "maturity", "rating", "cast", "director")
        }),
        ("Mise en avant", {
            "fields": ("is_featured", "is_trending"),
            "classes": ("collapse",),
        }),
        ("Médias", {
            "fields": ("poster", "poster_url", "backdrop", "backdrop_url", "video_url", "trailer_url")
        }),
    )

    @admin.display(description="Affiche")
    def poster_thumb(self, obj):
        src = obj.poster_src
        if not src:
            return "—"
        return format_html('<img src="{}" style="width:46px;height:68px;object-fit:cover;border-radius:4px"/>', src)

    @admin.display(description="Genres")
    def genres_list(self, obj):
        return ", ".join(g.name for g in obj.genres.all()[:3])

    @admin.action(description="✨ Mettre en avant (En vedette)")
    def mark_featured(self, request, queryset):
        n = queryset.update(is_featured=True)
        self.message_user(request, f"{n} titre(s) mis en avant.")

    @admin.action(description="Retirer de En vedette")
    def unmark_featured(self, request, queryset):
        queryset.update(is_featured=False)

    @admin.action(description="🔥 Marquer comme Tendance")
    def mark_trending(self, request, queryset):
        queryset.update(is_trending=True)

    @admin.action(description="Retirer des Tendances")
    def unmark_trending(self, request, queryset):
        queryset.update(is_trending=False)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "titles_count")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)

    @admin.display(description="Nb de titres")
    def titles_count(self, obj):
        return obj.titles.count()


@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ("title", "season", "number", "name", "duration_minutes")
    list_filter = ("title", "season")
    search_fields = ("title__title", "name")
    list_per_page = 50


@admin.register(WatchlistItem)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("profile", "title", "added_at")
    list_filter = ("added_at",)
    search_fields = ("profile__name", "title__title")
    date_hierarchy = "added_at"
    list_per_page = 50


@admin.register(WatchHistory)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ("profile", "title", "progress_seconds", "finished", "updated_at")
    list_filter = ("finished", "updated_at")
    search_fields = ("profile__name", "title__title")
    date_hierarchy = "updated_at"
    list_per_page = 50
