from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("mood", "0014_fix_color_nullable"),
    ]

    operations = [
        migrations.AddField(
            model_name="status",
            name="source",
            field=models.CharField(
                blank=True, db_index=True, max_length=128, null=True
            ),
        ),
    ]
