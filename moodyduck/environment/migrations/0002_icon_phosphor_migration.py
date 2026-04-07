from django.db import migrations

FA_TO_PHOSPHOR = {
    "fas fa-smog": "ph ph-cloud-fog",
    "fas fa-cloud": "ph ph-cloud",
    "fas fa-leaf": "ph ph-leaf",
    "fas fa-globe": "ph ph-globe",
    "fas fa-car": "ph ph-car",
    "fas fa-star": "ph ph-star",
    "fas fa-tint": "ph ph-drop",
}


def convert_icons(apps, schema_editor):
    for model_name in ["CO2Category"]:
        try:
            Model = apps.get_model("environment", model_name)
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
        ("environment", "0001_initial"),
    ]
    operations = [
        migrations.RunPython(convert_icons, reverse_convert),
    ]
