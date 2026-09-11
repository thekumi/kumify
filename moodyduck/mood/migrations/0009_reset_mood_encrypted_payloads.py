from django.db import migrations


def reset_encrypted_payloads(apps, schema_editor):
    Mood = apps.get_model("mood", "Mood")
    Mood.objects.all().update(encrypted_payload=None)


class Migration(migrations.Migration):
    dependencies = [
        ("mood", "0008_statusmedia_encrypted_payload"),
    ]

    operations = [
        migrations.RunPython(reset_encrypted_payloads, migrations.RunPython.noop),
    ]
