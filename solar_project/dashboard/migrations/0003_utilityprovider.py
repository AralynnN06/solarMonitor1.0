from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0002_solarsensor_metricreading_userprofile"),
    ]

    operations = [
        migrations.CreateModel(
            name="UtilityProvider",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=120, unique=True)),
                ("use_eia", models.BooleanField(default=True)),
                ("eia_state", models.CharField(blank=True, default="", max_length=2)),
                ("manual_rate_usd_per_kwh", models.FloatField(blank=True, null=True)),
            ],
            options={
                "ordering": ["name"],
            },
        ),
    ]

