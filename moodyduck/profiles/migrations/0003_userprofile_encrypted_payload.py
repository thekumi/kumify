from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0002_userprofile_address_userprofile_date_of_birth_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="encrypted_payload",
            field=models.JSONField(blank=True, null=True),
        ),
    ]
