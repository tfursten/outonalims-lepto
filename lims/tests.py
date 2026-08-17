import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Event, Location


class EventDetailViewTests(TestCase):
    def test_event_detail_handles_location_without_neighborhood(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        location = Location.objects.create(name="No Neighborhood Location")
        event = Event.objects.create(
            name="No Neighborhood Event",
            location=location,
            start_date=datetime.date(2026, 6, 1),
            end_date=datetime.date(2026, 6, 2),
        )

        self.client.force_login(user)
        response = self.client.get(reverse("lims:event_detail", args=(event.id,)))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No Neighborhood Event")
        self.assertContains(response, "Neighborhood")


class EventListViewTests(TestCase):
    def test_event_list_includes_export_buttons_without_undefined_editor(self):
        user = User.objects.create_user(username="viewer", password="test-pass")
        self.client.force_login(user)

        response = self.client.get(reverse("lims:event_list"))

        self.assertEqual(response.status_code, 200)
        for export_format in ("copy", "pdf", "csv", "excel"):
            self.assertContains(response, f"extend: '{export_format}'")
        self.assertNotContains(response, "editor: editor")
