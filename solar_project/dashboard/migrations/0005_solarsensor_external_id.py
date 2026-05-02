from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0004_utilityprovider_rate_source_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="solarsensor",
            name="external_id",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterUniqueTogether(
            name="solarsensor",
            unique_together={("user", "external_id"), ("user", "name")},
        ),
    ]

