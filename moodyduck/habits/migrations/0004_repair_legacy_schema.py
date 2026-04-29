from django.conf import settings
from django.db import migrations


def mysql_column_type(cursor, table_name, column_name):
    cursor.execute(f"SHOW COLUMNS FROM `{table_name}` LIKE %s", [column_name])
    row = cursor.fetchone()
    if row is None:
        raise RuntimeError(f"Column {table_name}.{column_name} does not exist.")
    return row[1]


def repair_habits_schema(apps, schema_editor):
    connection = schema_editor.connection
    Habit = apps.get_model("habits", "Habit")
    HabitLog = apps.get_model("habits", "HabitLog")
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))

    existing_tables = set(connection.introspection.table_names())

    if Habit._meta.db_table not in existing_tables:
        schema_editor.create_model(Habit)
        existing_tables.add(Habit._meta.db_table)
    elif connection.vendor == "mysql":
        with connection.cursor() as cursor:
            cursor.execute(f"ALTER TABLE `{Habit._meta.db_table}` ENGINE=InnoDB")

    with connection.cursor() as cursor:
        columns = {
            column.name
            for column in connection.introspection.get_table_description(
                cursor,
                Habit._meta.db_table,
            )
        }

        if "user_id" not in columns:
            if connection.vendor == "mysql":
                user_table = User._meta.db_table
                user_pk_type = mysql_column_type(cursor, user_table, "id")
                cursor.execute(
                    f"ALTER TABLE `{Habit._meta.db_table}` "
                    f"ADD COLUMN `user_id` {user_pk_type} NULL"
                )
            else:
                field = Habit._meta.get_field("user")
                field.default = None
                field.null = True
                schema_editor.add_field(Habit, field)

    if "user_id" not in columns:
        if Habit.objects.exists():
            users = list(User.objects.order_by("pk").values_list("pk", flat=True)[:2])
            if len(users) != 1:
                raise RuntimeError(
                    "Cannot backfill habits.user_id automatically because the legacy "
                    "database contains habits but does not map them to exactly one user."
                )
            Habit.objects.filter(user__isnull=True).update(user_id=users[0])

        if connection.vendor == "mysql":
            with connection.cursor() as cursor:
                user_table = User._meta.db_table
                user_pk_type = mysql_column_type(cursor, user_table, "id")
                cursor.execute(
                    f"ALTER TABLE `{Habit._meta.db_table}` "
                    f"MODIFY `user_id` {user_pk_type} NOT NULL"
                )
                cursor.execute(
                    f"ALTER TABLE `{Habit._meta.db_table}` "
                    "ADD INDEX `habits_habit_user_id_idx` (`user_id`)"
                )
                cursor.execute(
                    f"ALTER TABLE `{Habit._meta.db_table}` "
                    f"ADD CONSTRAINT `habits_habit_user_id_fk` FOREIGN KEY (`user_id`) "
                    f"REFERENCES `{user_table}` (`id`)"
                )

    if HabitLog._meta.db_table not in existing_tables:
        if connection.vendor == "mysql":
            with connection.cursor() as cursor:
                habit_pk_type = mysql_column_type(cursor, Habit._meta.db_table, "id")
                cursor.execute(
                    f"""
                    CREATE TABLE `{HabitLog._meta.db_table}` (
                        `id` BIGINT NOT NULL AUTO_INCREMENT,
                        `date` date NOT NULL,
                        `note` longtext NULL,
                        `habit_id` {habit_pk_type} NOT NULL,
                        PRIMARY KEY (`id`),
                        INDEX `habits_habitlog_habit_id_idx` (`habit_id`),
                        CONSTRAINT `habits_habitlog_habit_id_fk`
                            FOREIGN KEY (`habit_id`) REFERENCES `{Habit._meta.db_table}` (`id`)
                    ) ENGINE=InnoDB
                    """
                )
        else:
            schema_editor.create_model(HabitLog)


class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ("habits", "0003_alter_dailyhabitschedule_options_and_more"),
    ]

    operations = [
        migrations.RunPython(repair_habits_schema, migrations.RunPython.noop),
    ]
