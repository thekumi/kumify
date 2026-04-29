from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from moodyduck.mood.models import Activity, Mood, Status
from moodyduck.health.models import HealthLog, HealthParameter, HealthRecord


class HealthLogApiTests(APITestCase):
    def setUp(self):
        self.host = settings.ALLOWED_HOSTS[0]
        self.user = get_user_model().objects.create_user(
            username="api-user",
            password="secret",
        )
        self.other_user = get_user_model().objects.create_user(
            username="other-user",
            password="secret",
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("health-log-list")

    def test_create_health_log_with_records(self):
        weight = HealthParameter.objects.create(
            user=self.user,
            name="Weight",
            unit="kg",
        )
        pulse = HealthParameter.objects.create(
            user=self.user,
            name="Pulse",
            unit="bpm",
        )

        response = self.client.post(
            self.url,
            {
                "notes": "Morning check-in",
                "records": [
                    {"parameter": weight.pk, "value": "71.4"},
                    {"parameter": pulse.pk, "value": "58"},
                ],
            },
            format="json",
            HTTP_HOST=self.host,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(HealthLog.objects.filter(user=self.user).count(), 1)

        log = HealthLog.objects.get(user=self.user)
        records = HealthRecord.objects.filter(log=log).order_by("parameter__name")
        self.assertEqual(records.count(), 2)
        self.assertEqual(records[0].parameter, pulse)
        self.assertEqual(records[0].value, Decimal("58"))
        self.assertEqual(records[1].parameter, weight)
        self.assertEqual(records[1].value, Decimal("71.4"))

        self.assertEqual(len(response.data["records"]), 2)
        self.assertCountEqual(
            [record["parameter"]["name"] for record in response.data["records"]],
            ["Pulse", "Weight"],
        )

    def test_create_health_log_rejects_foreign_parameter(self):
        foreign_parameter = HealthParameter.objects.create(
            user=self.other_user,
            name="Private metric",
            unit="u",
        )

        response = self.client.post(
            self.url,
            {
                "records": [
                    {"parameter": foreign_parameter.pk, "value": "1"},
                ],
            },
            format="json",
            HTTP_HOST=self.host,
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(HealthLog.objects.filter(user=self.user).count(), 0)


class StatusApiTests(APITestCase):
    def setUp(self):
        self.host = settings.ALLOWED_HOSTS[0]
        self.user = get_user_model().objects.create_user(
            username="status-user",
            password="secret",
        )
        self.client.force_authenticate(user=self.user)
        self.url = reverse("status-list")

    def test_create_status_with_activities(self):
        mood = Mood.objects.create(user=self.user, name="Okay", value=3)
        walk = Activity.objects.create(user=self.user, name="Walk")
        reading = Activity.objects.create(user=self.user, name="Reading")

        response = self.client.post(
            self.url,
            {
                "mood": mood.pk,
                "title": "Afternoon reset",
                "text": "Got outside for a bit.",
                "activity_ids": [walk.pk, reading.pk],
            },
            format="json",
            HTTP_HOST=self.host,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        status_obj = Status.objects.get(user=self.user)
        self.assertEqual(status_obj.mood, mood)
        self.assertCountEqual(
            [activity.name for activity in status_obj.activity_set],
            ["Walk", "Reading"],
        )
        self.assertCountEqual(
            [activity["name"] for activity in response.data["activities"]],
            ["Walk", "Reading"],
        )


class ReferenceDataApiTests(APITestCase):
    def setUp(self):
        self.host = settings.ALLOWED_HOSTS[0]
        self.user = get_user_model().objects.create_user(
            username="reference-user",
            password="secret",
        )
        self.client.force_authenticate(user=self.user)

    def test_create_mood_activity_habit_and_parameter(self):
        mood_response = self.client.post(
            reverse("mood-list"),
            {
                "name": "Focused",
                "value": 4,
                "icon": "ph ph-brain",
                "color": "#123456",
            },
            format="json",
            HTTP_HOST=self.host,
        )
        activity_response = self.client.post(
            reverse("activity-list"),
            {
                "name": "Reading",
                "icon": "ph ph-book-open",
                "color": "#654321",
            },
            format="json",
            HTTP_HOST=self.host,
        )
        habit_response = self.client.post(
            reverse("habit-list"),
            {
                "name": "Stretch",
                "icon": "ph ph-heart",
                "color": "#abcdef",
                "description": "Five minutes",
            },
            format="json",
            HTTP_HOST=self.host,
        )
        parameter_response = self.client.post(
            reverse("health-parameter-list"),
            {
                "name": "Pulse",
                "unit": "bpm",
                "icon": "ph ph-heartbeat",
            },
            format="json",
            HTTP_HOST=self.host,
        )

        self.assertEqual(mood_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(activity_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(habit_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(parameter_response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(Mood.objects.filter(user=self.user, name="Focused").count(), 1)
        self.assertEqual(Activity.objects.filter(user=self.user, name="Reading").count(), 1)
