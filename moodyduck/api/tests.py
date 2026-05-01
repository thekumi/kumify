from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from moodyduck.dreams.models import Dream, DreamMedia
from moodyduck.friends.models import Person
from moodyduck.health.models import BasicMedicalInfo, Vaccination
from moodyduck.mood.models import Activity, Mood, Status, StatusMedia
from moodyduck.health.models import HealthLog, HealthParameter, HealthRecord
from moodyduck.profiles.models import EmergencyAccessLog


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

    def test_status_attachments_upload_and_delete(self):
        status_obj = Status.objects.create(
            user=self.user,
            title="Attachment test",
            text="With image",
        )

        upload_response = self.client.post(
            reverse("status-attachments", kwargs={"pk": status_obj.pk}),
            {
                "file": SimpleUploadedFile(
                    "mood.png",
                    b"fake-image-data",
                    content_type="image/png",
                )
            },
            format="multipart",
            HTTP_HOST=self.host,
        )

        self.assertEqual(upload_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(StatusMedia.objects.filter(status=status_obj).count(), 1)

        status_response = self.client.get(
            reverse("status-detail", kwargs={"pk": status_obj.pk}),
            HTTP_HOST=self.host,
        )
        self.assertEqual(len(status_response.data["attachments"]), 1)

        attachment_id = status_response.data["attachments"][0]["id"]
        delete_response = self.client.delete(
            reverse(
                "status-delete-attachment",
                kwargs={"pk": status_obj.pk, "attachment_id": attachment_id},
            ),
            HTTP_HOST=self.host,
        )

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(StatusMedia.objects.filter(status=status_obj).count(), 0)


class DreamApiTests(APITestCase):
    def setUp(self):
        self.host = settings.ALLOWED_HOSTS[0]
        self.user = get_user_model().objects.create_user(
            username="dream-user",
            password="secret",
        )
        self.client.force_authenticate(user=self.user)

    def test_dream_attachments_upload_and_delete(self):
        dream = Dream.objects.create(
            user=self.user,
            title="Flying",
            content="Dreamed about flying over a city.",
            type=0,
        )

        upload_response = self.client.post(
            reverse("dream-attachments", kwargs={"pk": dream.pk}),
            {
                "file": SimpleUploadedFile(
                    "dream.jpg",
                    b"fake-jpeg-data",
                    content_type="image/jpeg",
                )
            },
            format="multipart",
            HTTP_HOST=self.host,
        )

        self.assertEqual(upload_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DreamMedia.objects.filter(dream=dream).count(), 1)

        detail_response = self.client.get(
            reverse("dream-detail", kwargs={"pk": dream.pk}),
            HTTP_HOST=self.host,
        )
        self.assertEqual(len(detail_response.data["attachments"]), 1)

        attachment_id = detail_response.data["attachments"][0]["id"]
        delete_response = self.client.delete(
            reverse(
                "dream-delete-attachment",
                kwargs={"pk": dream.pk, "attachment_id": attachment_id},
            ),
            HTTP_HOST=self.host,
        )

        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(DreamMedia.objects.filter(dream=dream).count(), 0)


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


class EmergencyApiTests(APITestCase):
    def setUp(self):
        self.host = settings.ALLOWED_HOSTS[0]
        self.user = get_user_model().objects.create_user(
            username="emergency-user",
            password="secret",
        )
        self.client.force_authenticate(user=self.user)

    def test_emergency_profile_and_access_logs(self):
        profile = self.user.userprofile
        profile.legal_name = "Duck User"
        profile.phone = "+123"
        profile.save()
        BasicMedicalInfo.objects.create(
            user=self.user,
            blood_type="O+",
            allergies="Peanuts",
            medical_notes="Carries inhaler",
        )
        Person.objects.create(
            user=self.user,
            name="Alex Friend",
            phone="+999",
            relationship="Sibling",
            emergency_contact=True,
        )
        Vaccination.objects.create(
            user=self.user,
            name="Flu shot 2024",
            target_disease="Influenza",
            administered_on="2024-10-01",
        )
        Vaccination.objects.create(
            user=self.user,
            name="Flu shot 2025",
            target_disease="Influenza",
            administered_on="2025-10-01",
        )
        Vaccination.objects.create(
            user=self.user,
            name="COVID booster",
            target_disease="COVID-19",
            administered_on="2025-03-05",
        )

        profile_response = self.client.get(
            reverse("emergency-profile"),
            HTTP_HOST=self.host,
        )
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        self.assertEqual(profile_response.data["blood_type"], "O+")
        self.assertEqual(profile_response.data["contacts"][0]["relationship"], "Sibling")
        self.assertEqual(len(profile_response.data["vaccinations"]), 2)
        self.assertEqual(profile_response.data["vaccinations"][0]["target_disease"], "COVID-19")
        self.assertEqual(profile_response.data["vaccinations"][1]["name"], "Flu shot 2025")

        log_response = self.client.post(
            reverse("emergency-access-log-list"),
            {"source": "android", "method": "locked_screen", "details": "offline cache"},
            format="json",
            HTTP_HOST=self.host,
        )
        self.assertEqual(log_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(EmergencyAccessLog.objects.filter(user=self.user).count(), 1)


class FriendsApiTests(APITestCase):
    def setUp(self):
        self.host = settings.ALLOWED_HOSTS[0]
        self.user = get_user_model().objects.create_user(
            username="friends-user",
            password="secret",
        )
        self.client.force_authenticate(user=self.user)

    def test_create_friend(self):
        response = self.client.post(
            reverse("friend-list"),
            {
                "name": "Alex Friend",
                "phone": "+999",
                "relationship": "Sibling",
                "emergency_contact": True,
            },
            format="json",
            HTTP_HOST=self.host,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Person.objects.filter(user=self.user, name="Alex Friend").count(), 1)
        self.assertTrue(Person.objects.get(user=self.user, name="Alex Friend").emergency_contact)
