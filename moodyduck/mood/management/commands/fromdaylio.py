import csv
from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from moodyduck.mood.models import Activity, Mood, Status, StatusActivity

DATE_FORMAT = "%Y-%m-%d %I:%M %p"


class Command(BaseCommand):
    help = "Import .csv from Daylio"

    def add_arguments(self, parser):
        parser.add_argument("username")
        parser.add_argument("path")

    def handle(self, *args, **options):
        try:
            user = get_user_model().objects.get(username=options["username"])
            with open(options["path"], mode="r", encoding="utf-8-sig") as infile:
                reader = csv.DictReader(infile)
                for row in reader:
                    timestamp = datetime.strptime(
                        f"{row['full_date']} {row['time']}", DATE_FORMAT
                    ).replace(tzinfo=timezone.utc)
                    activities = [a.strip() for a in row["activities"].split("|")]

                    try:
                        mood = Mood.objects.get(user=user, name__iexact=row["mood"])
                    except Mood.DoesNotExist:
                        mood = Mood.objects.create(user=user, name=row["mood"], value=0)

                    status = Status.objects.create(
                        user=user,
                        timestamp=timestamp,
                        mood=mood,
                        title=row["note_title"],
                        text=row["note"],
                    )

                    for activity in activities:
                        if activity:
                            try:
                                aobj = Activity.objects.get(
                                    user=user, name__iexact=activity
                                )
                            except Activity.DoesNotExist:
                                aobj = Activity.objects.create(user=user, name=activity)

                            StatusActivity.objects.create(status=status, activity=aobj)

        except FileNotFoundError:
            raise CommandError(f'File "{options["path"]}" does not exist')
        except get_user_model().DoesNotExist:
            raise CommandError(f'User "{options["user"]}" does not exist')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully imported data for user "{options["username"]}"'
            )
        )
