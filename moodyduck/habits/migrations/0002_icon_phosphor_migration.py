from django.db import migrations

FA_TO_PHOSPHOR = {
    "fas fa-user-clock": "ph ph-user-gear",
    "fas fa-star": "ph ph-star",
    "fas fa-check": "ph ph-check",
    "fas fa-heart": "ph ph-heart",
    "fas fa-calendar": "ph ph-calendar",
    "fas fa-clock": "ph ph-clock",
    "fas fa-leaf": "ph ph-leaf",
    "fas fa-brain": "ph ph-brain",
    "fas fa-smile": "ph ph-smiley",
    "fas fa-book": "ph ph-book-open",
    "fas fa-globe": "ph ph-globe",
}


def convert_icons(apps, schema_editor):
    try:
        Model = apps.get_model("habits", "Habit")
        for obj in Model.objects.all():
            new_icon = FA_TO_PHOSPHOR.get(obj.icon)
            if new_icon:
                obj.icon = new_icon
                obj.save(update_fields=["icon"])
    except Exception:
        pass


def reverse_convert(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("habits", "0001_initial"),
    ]
    operations = [
        migrations.RunPython(convert_icons, reverse_convert),
    ]
