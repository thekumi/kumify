from django.db import migrations


def repair_health_schema(apps, schema_editor):
    connection = schema_editor.connection
    HealthLog = apps.get_model("health", "HealthLog")
    HealthRecord = apps.get_model("health", "HealthRecord")

    existing_tables = set(connection.introspection.table_names())

    if HealthLog._meta.db_table not in existing_tables:
        schema_editor.create_model(HealthLog)
        existing_tables.add(HealthLog._meta.db_table)

    if HealthRecord._meta.db_table not in existing_tables:
        schema_editor.create_model(HealthRecord)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("health", "0003_alter_healthparameter_icon_alter_medication_icon_and_more"),
    ]

    operations = [
        migrations.RunPython(repair_health_schema, migrations.RunPython.noop),
    ]
