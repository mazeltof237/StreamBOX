from django.conf import settings
from django.db import models
from django.utils import timezone

AVATAR_GRADIENTS = [
    ("kids", "Rouge"),
    ("fafi", "Bleu"),
    ("nina", "Violet"),
    ("nicky", "Vert eau"),
    ("gold", "Or"),
    ("dark", "Sombre"),
]


class Profile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profiles")
    name = models.CharField(max_length=40)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    avatar_preset = models.CharField(max_length=10, choices=AVATAR_GRADIENTS, default="fafi")
    is_kid = models.BooleanField(default=False)
    pin = models.CharField(max_length=4, blank=True, default="", help_text="Code PIN 4 chiffres (optionnel)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        unique_together = ("user", "name")

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    @property
    def initial(self):
        return self.name[:1].upper() if self.name else "?"


class Plan(models.Model):
    code = models.SlugField(max_length=20, unique=True)
    name = models.CharField(max_length=40)
    price_eur = models.DecimalField(max_digits=6, decimal_places=2)
    quality = models.CharField(max_length=20, default="HD")
    max_profiles = models.PositiveSmallIntegerField(default=2)
    simultaneous_streams = models.PositiveSmallIntegerField(default=1)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["price_eur"]

    def __str__(self):
        return f"{self.name} ({self.price_eur} €)"


class Subscription(models.Model):
    STATUS_CHOICES = [("active", "Active"), ("canceled", "Annulée"), ("past_due", "Impayée")]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscription")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    started_at = models.DateTimeField(default=timezone.now)
    renews_at = models.DateTimeField(default=timezone.now)
    stripe_id = models.CharField(max_length=120, blank=True, default="")

    def is_active(self):
        return self.status == "active" and self.renews_at >= timezone.now()

    def __str__(self):
        return f"{self.user.username} → {self.plan.name} ({self.status})"


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    method = models.CharField(max_length=20, default="card")
    succeeded = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
