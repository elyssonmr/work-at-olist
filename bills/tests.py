from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from bills.models import CallRecord



class TelephoneBillTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.last_month = timezone.now() - timedelta(days=30)
        self.start_record1 = CallRecord.objects.create(
            record_type="S", timestamp=timezone.now(), call_id=1,
            source="12345678", destination="87654321")
        self.start_record2 = CallRecord.objects.create(
            record_type="S", timestamp=timezone.now(), call_id=2,
            source="12345678", destination="87654321")
        self.end_record1 = CallRecord.objects.create(
            record_type="E", timestamp=timezone.now(), call_id=1,
            source="12345678", destination="87654321")
        self.end_record2 = CallRecord.objects.create(
            record_type="E", timestamp=timezone.now(), call_id=2,
            source="12345678", destination="87654321")
        self.end_record3 = CallRecord.objects.create(
            record_type="E", timestamp=timezone.now(), call_id=3,
            source="12345678", destination="87654321")
        # last month records
        self.start_record4 = CallRecord.objects.create(
            record_type="S", timestamp=self.last_month, call_id=4,
            source="12345678", destination="87654321")
        self.end_record4 = CallRecord.objects.create(
            record_type="E", timestamp=self.last_month, call_id=4,
            source="12345678", destination="87654321")


    def test_get_bill_records(self):
        expected_records = [
            (self.start_record1, self.end_record1),
            (self.start_record2, self.end_record2)
        ]
        bill_records = CallRecord.objects.get_bill_records("12345678")

        self.assertEqual(expected_records, bill_records)

    def test_get_bill_records_with_reference_period(self):
        expected_records = [
            (self.start_record4, self.end_record4)
        ]
        billing_cycle = f"{self.last_month.month:02}/{self.last_month.year}"
        bill_records = CallRecord.objects.get_bill_records(
            "12345678", billing_cycle)

        self.assertEqual(expected_records, bill_records)
