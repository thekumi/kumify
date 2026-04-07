from django.db import migrations

FA_TO_PHOSPHOR = {
    "fas fa-star": "ph ph-star",
    "fas fa-check": "ph ph-check",
    "fas fa-heart": "ph ph-heart",
    "fas fa-smile": "ph ph-smiley",
    "fas fa-clock": "ph ph-clock",
    "fas fa-calendar": "ph ph-calendar",
    "fas fa-bell": "ph ph-bell",
    "fas fa-list": "ph ph-list-bullets",
    "fas fa-tag": "ph ph-tag",
    "fas fa-tags": "ph ph-tag",
    "fas fa-cog": "ph ph-gear",
    "fas fa-edit": "ph ph-pencil-simple",
    "fas fa-trash": "ph ph-trash",
    "fas fa-trash-alt": "ph ph-trash",
    "fas fa-brain": "ph ph-brain",
    "fas fa-feather-alt": "ph ph-feather",
    "fas fa-leaf": "ph ph-leaf",
    "fas fa-globe": "ph ph-globe",
    "fas fa-heartbeat": "ph ph-heartbeat",
    "fas fa-chart-pie": "ph ph-chart-pie",
}


def convert_icons(apps, schema_editor):
    for model_name in ["Mood", "ActivityCategory", "Activity", "AspectRating"]:
        try:
            Model = apps.get_model("mood", model_name)
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
        ("mood", "0003_alter_mood_value"),
    ]
    operations = [
        migrations.RunPython(convert_icons, reverse_convert),
    ]
