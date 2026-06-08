"""Admin personnalisé — Comptes, profils, abonnements (bonus)."""
from django.contrib import admin
from django.utils.html import format_html
from .models import Profile, Plan, Subscription, Payment


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("avatar_chip", "name", "user", "is_kid", "has_pin", "created_at")
    list_display_links = ("avatar_chip", "name")
    list_filter = ("is_kid", "avatar_preset")
    search_fields = ("name", "user__username", "user__email")
    list_per_page = 50

    @admin.display(description="Avatar")
    def avatar_chip(self, obj):
        colors = {"kids": "#ff4d4d", "fafi": "#3b82f6", "nina": "#a855f7",
                  "nicky": "#14b8a6", "gold": "#facc15", "dark": "#444"}
        c = colors.get(obj.avatar_preset, "#888")
        return format_html(
            '<div style="width:34px;height:34px;border-radius:6px;background:{};color:#000;'
            'display:grid;place-items:center;font-weight:800">{}</div>',
            c, obj.initial,
        )

    @admin.display(boolean=True, description="PIN")
    def has_pin(self, obj):
        return bool(obj.pin)


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "price_badge", "quality",
                    "max_profiles", "simultaneous_streams", "is_active")
    list_filter = ("is_active", "quality")
    prepopulated_fields = {"code": ("name",)}
    list_editable = ("is_active",)

    @admin.display(description="Prix")
    def price_badge(self, obj):
        return format_html(
            '<span style="background:#00bf63;color:#000;padding:2px 8px;'
            'border-radius:4px;font-weight:700">{} €</span>', obj.price_eur,
        )


@admin.register(Subscription)
class SubAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "status_badge", "started_at", "renews_at")
    list_filter = ("status", "plan")
    search_fields = ("user__username", "user__email")
    date_hierarchy = "started_at"
    list_per_page = 50

    @admin.display(description="Statut")
    def status_badge(self, obj):
        colors = {"active": "#00bf63", "canceled": "#ff6b6b", "past_due": "#facc15"}
        c = colors.get(obj.status, "#888")
        return format_html(
            '<span style="background:{};color:#000;padding:3px 10px;'
            'border-radius:12px;font-size:11px;font-weight:700">{}</span>',
            c, obj.get_status_display(),
        )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "plan", "amount", "method", "succeeded", "created_at")
    list_filter = ("succeeded", "method", "plan")
    search_fields = ("user__username",)
    date_hierarchy = "created_at"
    list_per_page = 50
