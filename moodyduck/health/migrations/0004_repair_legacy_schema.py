from django.db import migrations


def mysql_column_type(cursor, table_name, column_name):
    cursor.execute(f"SHOW COLUMNS FROM `{table_name}` LIKE %s", [column_name])
    row = cursor.fetchone()
    if row is None:
        raise RuntimeError(f"Column {table_name}.{column_name} does not exist.")
    return row[1]


def repair_health_schema(apps, schema_editor):
    connection = schema_editor.connection
    HealthLog = apps.get_model("health", "HealthLog")
    HealthRecord = apps.get_model("health", "HealthRecord")
    User = apps.get_model("auth", "User")

    existing_tables = set(connection.introspection.table_names())

    if HealthLog._meta.db_table not in existing_tables:
        if connection.vendor == "mysql":
            with connection.cursor() as cursor:
                cursor.execute("ALTER TABLE `health_healthparameter` ENGINE=InnoDB")
                user_pk_type = mysql_column_type(cursor, User._meta.db_table, "id")
                cursor.execute(
                    f"""
                    CREATE TABLE `{HealthLog._meta.db_table}` (
                        `id` BIGINT NOT NULL AUTO_INCREMENT,
                        `recorded_at` datetime(6) NOT NULL,
                        `notes` longtext NULL,
                        `user_id` {user_pk_type} NOT NULL,
                        PRIMARY KEY (`id`),
                        INDEX `health_healthlog_user_id_idx` (`user_id`),
                        CONSTRAINT `health_healthlog_user_id_fk`
                            FOREIGN KEY (`user_id`) REFERENCES `{User._meta.db_table}` (`id`)
                    ) ENGINE=InnoDB
                    """
                )
        else:
            schema_editor.create_model(HealthLog)
        existing_tables.add(HealthLog._meta.db_table)

    if HealthRecord._meta.db_table not in existing_tables:
        if connection.vendor == "mysql":
            with connection.cursor() as cursor:
                parameter_pk_type = mysql_column_type(
                    cursor,
                    apps.get_model("health", "HealthParameter")._meta.db_table,
                    "id",
                )
                cursor.execute(
                    f"""
                    CREATE TABLE `{HealthRecord._meta.db_table}` (
                        `id` BIGINT NOT NULL AUTO_INCREMENT,
                        `value` decimal(12,6) NULL,
                        `comment` longtext NULL,
                        `log_id` BIGINT NOT NULL,
                        `parameter_id` {parameter_pk_type} NOT NULL,
                        PRIMARY KEY (`id`),
                        INDEX `health_healthrecord_log_id_idx` (`log_id`),
                        INDEX `health_healthrecord_parameter_id_idx` (`parameter_id`),
                        CONSTRAINT `health_healthrecord_log_id_fk`
                            FOREIGN KEY (`log_id`) REFERENCES `{HealthLog._meta.db_table}` (`id`),
                        CONSTRAINT `health_healthrecord_parameter_id_fk`
                            FOREIGN KEY (`parameter_id`) REFERENCES `health_healthparameter` (`id`)
                    ) ENGINE=InnoDB
                    """
                )
        else:
            schema_editor.create_model(HealthRecord)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("health", "0003_alter_healthparameter_icon_alter_medication_icon_and_more"),
    ]

    operations = [
        migrations.RunPython(repair_health_schema, migrations.RunPython.noop),
    ]
