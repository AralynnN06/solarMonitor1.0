from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("dashboard", "0003_utilityprovider"),
    ]

    operations = [
        migrations.AddField(
            model_name="utilityprovider",
            name="rate_source_url",
            field=models.URLField(blank=True, default=""),
        ),
    ]

