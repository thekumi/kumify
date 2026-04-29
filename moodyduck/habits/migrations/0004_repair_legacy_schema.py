from django.conf import settings
from django.db import migrations


def repair_habits_schema(apps, schema_editor):
    connection = schema_editor.connection
    Habit = apps.get_model("habits", "Habit")
    HabitLog = apps.get_model("habits", "HabitLog")
    User = apps.get_model(*settings.AUTH_USER_MODEL.split("."))

    existing_tables = set(connection.introspection.table_names())

    if Habit._meta.db_table not in existing_tables:
        schema_editor.create_model(Habit)
        existing_tables.add(Habit._meta.db_table)

    with connection.cursor() as cursor:
        columns = {
            column.name
            for column in connection.introspection.get_table_description(
                cursor,
                Habit._meta.db_table,
            )
        }

    if "user_id" not in columns:
        field = Habit._meta.get_field("user")
        field.default = None
        field.null = True
        schema_editor.add_field(Habit, field)

        if Habit.objects.exists():
            users = list(User.objects.order_by("pk").values_list("pk", flat=True)[:2])
            if len(users) != 1:
                raise RuntimeError(
                    "Cannot backfill habits.user_id automatically because the legacy "
                    "database contains habits but does not map them to exactly one user."
                )
            Habit.objects.filter(user__isnull=True).update(user_id=users[0])

        with connection.cursor() as cursor:
            vendor = connection.vendor
            if vendor == "mysql":
                cursor.execute(
                    "ALTER TABLE habits_habit MODIFY user_id integer NOT NULL"
                )
            elif vendor == "sqlite":
                # SQLite keeps the column nullable after ADD COLUMN; the ORM field state
                # is enough for local development, and production uses MySQL.
                pass

    if HabitLog._meta.db_table not in existing_tables:
        schema_editor.create_model(HabitLog)


class Migration(migrations.Migration):
    dependencies = [
        ("habits", "0003_alter_dailyhabitschedule_options_and_more"),
    ]

    operations = [
        migrations.RunPython(repair_habits_schema, migrations.RunPython.noop),
    ]
