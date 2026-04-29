from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

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
