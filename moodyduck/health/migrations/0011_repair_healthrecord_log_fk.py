from django.db import migrations


def add_log_id(apps, schema_editor):
    connection = schema_editor.connection
    HealthRecord = apps.get_model("health", "HealthRecord")
    HealthLog = apps.get_model("health", "HealthLog")

    hr_table = HealthRecord._meta.db_table
    hl_table = HealthLog._meta.db_table

    with connection.cursor() as cursor:
        existing = {
            c.name
            for c in connection.introspection.get_table_description(cursor, hr_table)
        }

    if "log_id" in existing:
        return

    if connection.vendor != "mysql":
        return

    with connection.cursor() as cursor:
        cursor.execute(f"ALTER TABLE `{hr_table}` ADD COLUMN `log_id` BIGINT NULL")

        # Each orphaned record gets its own synthetic log so that the log's
        # recorded_at can later be set correctly if needed.
        cursor.execute(
            f"""
            SELECT r.id, p.user_id
            FROM `{hr_table}` r
            JOIN `health_healthparameter` p ON r.parameter_id = p.id
            WHERE r.log_id IS NULL
            """
        )
        rows = cursor.fetchall()

        if rows:
            from django.utils.timezone import now

            ts = now()
            for record_id, user_id in rows:
                cursor.execute(
                    f"INSERT INTO `{hl_table}` (recorded_at, user_id) VALUES (%s, %s)",
                    [ts, user_id],
                )
                log_id = cursor.lastrowid
                cursor.execute(
                    f"UPDATE `{hr_table}` SET log_id = %s WHERE id = %s",
                    [log_id, record_id],
                )

        cursor.execute(f"ALTER TABLE `{hr_table}` MODIFY `log_id` BIGINT NOT NULL")
        cursor.execute(
            f"ALTER TABLE `{hr_table}` ADD CONSTRAINT `health_healthrecord_log_id_fk`"
            f" FOREIGN KEY (`log_id`) REFERENCES `{hl_table}` (`id`) ON DELETE CASCADE"
        )


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("health", "0010_alter_healthparameter_icon_null"),
    ]

    operations = [
        migrations.RunPython(add_log_id, migrations.RunPython.noop),
    ]
