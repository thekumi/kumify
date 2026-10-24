from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mood", "0015_status_source"),
    ]

    operations = [
        migrations.AddField(
            model_name="statusmedia",
            name="source",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
