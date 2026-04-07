from django.db import migrations

FA_TO_PHOSPHOR = {
    "fas fa-tablets": "ph ph-pill",
    "fas fa-pills": "ph ph-pill",
    "fas fa-heart": "ph ph-heart",
    "fas fa-heartbeat": "ph ph-heartbeat",
    "fas fa-brain": "ph ph-brain",
    "fas fa-clock": "ph ph-clock",
    "fas fa-calendar": "ph ph-calendar",
    "fas fa-star": "ph ph-star",
    "fas fa-check": "ph ph-check",
    "fas fa-tint": "ph ph-drop",
    "fas fa-sliders-h": "ph ph-sliders-horizontal",
    "fas fa-balance-scale": "ph ph-scales",
}


def convert_icons(apps, schema_editor):
    for model_name in ["Medication", "HealthParameter"]:
        try:
            Model = apps.get_model("health", model_name)
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
        ("health", "0001_initial"),
    ]
    operations = [
        migrations.RunPython(convert_icons, reverse_convert),
    ]
