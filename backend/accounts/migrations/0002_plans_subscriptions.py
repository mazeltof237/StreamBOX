from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.AddField(
            model_name="profile",
            name="pin",
            field=models.CharField(blank=True, default="", max_length=4),
        ),
        migrations.CreateModel(
            name="Plan",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("code", models.SlugField(max_length=20, unique=True)),
                ("name", models.CharField(max_length=40)),
                ("price_eur", models.DecimalField(decimal_places=2, max_digits=6)),
                ("quality", models.CharField(default="HD", max_length=20)),
                ("max_profiles", models.PositiveSmallIntegerField(default=2)),
                ("simultaneous_streams", models.PositiveSmallIntegerField(default=1)),
                ("description", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["price_eur"]},
        ),
        migrations.CreateModel(
            name="Subscription",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("status", models.CharField(choices=[("active", "Active"), ("canceled", "Annulée"), ("past_due", "Impayée")], default="active", max_length=10)),
                ("started_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("renews_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("stripe_id", models.CharField(blank=True, default="", max_length=120)),
                ("plan", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="subscriptions", to="accounts.plan")),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="subscription", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=8)),
                ("method", models.CharField(default="card", max_length=20)),
                ("succeeded", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("plan", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="accounts.plan")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payments", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
