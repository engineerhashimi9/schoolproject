from django.core.management import call_command
from django.test import TestCase

from dashboard.models import Student


class SeedTestDataTests(TestCase):
    def test_seed_test_data_creates_100_students(self):
        call_command("seed_test_data", count=100)
        self.assertGreaterEqual(Student.objects.count(), 100)
