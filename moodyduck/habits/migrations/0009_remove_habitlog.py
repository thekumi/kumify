from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("habits", "0008_habit_updated_at_habitlog_updated_at"),
    ]

    operations = [
        migrations.DeleteModel(name="HabitLog"),
    ]
