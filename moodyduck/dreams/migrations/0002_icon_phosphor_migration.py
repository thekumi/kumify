from django.db import migrations

FA_TO_PHOSPHOR = {
    "fas fa-bed": "ph ph-bed",
    "fas fa-star": "ph ph-star",
    "fas fa-moon": "ph ph-moon",
    "fas fa-feather-alt": "ph ph-feather",
    "fas fa-leaf": "ph ph-leaf",
    "fas fa-heart": "ph ph-heart",
    "fas fa-brain": "ph ph-brain",
    "fas fa-cloud": "ph ph-cloud",
    "fas fa-clock": "ph ph-clock",
    "fas fa-smile": "ph ph-smiley",
}


def convert_icons(apps, schema_editor):
    for model_name in ["Theme"]:
        try:
            Model = apps.get_model("dreams", model_name)
            for obj in Model.objects.all():
                new_icon = FA_TO_PHOSPHOR.get(obj.icon)
                if new_icon:
                    obj.icon = new_icon
                    obj.save(update_fields=["icon"])
        except Exception:
            pass
    try:
        Model = apps.get_model("dreams", "ThemeRating")
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
        ("dreams", "0001_initial"),
    ]
    operations = [
        migrations.RunPython(convert_icons, reverse_convert),
    ]
