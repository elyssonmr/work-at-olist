from decimal import Decimal
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from bills.models import CallRecord, Bill



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


class BillCreateTestCase(TestCase):
    def test_create_bill(self):
        subscriber = "12345678"
        start_record = CallRecord.objects.create(
            record_type="S", timestamp=timezone.now(), call_id=1,
            source=subscriber, destination="87654321")
        end_record = CallRecord.objects.create(
            record_type="E", timestamp=timezone.now(), call_id=1,
            source=subscriber, destination="87654321")
        records = [(start_record, end_record)]
        standing_charge = Decimal("0.36")
        minute_charge = Decimal("0.09")
        now = timezone.now()
        period = f"{now.month:02}/{now.year}"

        bill = Bill.objects.create_bill(
            subscriber, records, period, standing_charge, minute_charge)

        self.assertEqual(bill.pk, 1)
        self.assertEqual([start_record, end_record], list(bill.records.all()))


class BillCalculateBillTestCase(TestCase):
    def setUp(self):
        now = timezone.now()
        call_id = 1
        record1 = self._setup_test(timedelta(minutes=5, seconds=10), 15, call_id=call_id)
        call_id += 1
        record2 = self._setup_test(timedelta(minutes=10, seconds=50), 21, 57, 13, call_id=call_id)
        records = [record1, record2]
        standing_charge = Decimal("0.36")
        minute_charge = Decimal("0.09")
        period = f"{now.month:02}/{now.year}"
        self.bill = Bill.objects.create_bill(
            "12346578", records, period, standing_charge, minute_charge
        )
        
    def _setup_test(self, call_duration, start_hour=0, start_minute=0,
                    start_second=0, call_id=1):
        call_time = timezone.now()
        call_time = call_time.replace(
            hour=start_hour, minute=start_minute, second=start_second)
        start_record = CallRecord.objects.create(
            record_type="S", timestamp=call_time, call_id=call_id,
            source="12345678", destination="87654321"
        )
        end_record = CallRecord.objects.create(
            record_type="E", timestamp=call_time + call_duration,
            call_id=call_id, source="12345678", destination="87654321"
        )
        return start_record, end_record

    def test_calculate_bill(self):
        expected_total = Decimal("1.35")
        self.bill.calculate()

        self.assertTrue(self.bill.is_calculated)
        self.assertEqual(self.bill.total_price, expected_total)
