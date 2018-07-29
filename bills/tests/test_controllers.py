from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from bills.models import CallRecord
from bills.controllers import BillCalculator


class BillCalculatorInstanceTestCase(TestCase):
    def test_instance(self):
        instance = BillCalculator([], Decimal("0.36"), Decimal("0.09"))

        self.assertEqual(instance._records, [])
        self.assertEqual(instance._standing_charge, Decimal("0.36"))
        self.assertEqual(instance._minute_value, Decimal("0.09"))

class BillCalculatorChargeTestCase(TestCase):
    def setUp(self):
        super().setUp()
        standing_charge = Decimal("0.36")
        minute_value = Decimal("0.09")
        self.controller = BillCalculator([], standing_charge, minute_value)

    def _setup_test(self, call_duration, start_hour=0, start_minute=0,
                    start_second=0):
        call_time = timezone.now()
        call_time = call_time.replace(
            hour=start_hour, minute=start_minute, second=start_second)
        start_record = CallRecord.objects.create(
            record_type="S", timestamp=call_time, call_id=1,
            source="12345678", destination="87654321"
        )
        end_record = CallRecord.objects.create(
            record_type="E", timestamp=call_time + call_duration,
            call_id=1, source="12345678", destination="87654321"
        )
        return start_record, end_record

    def test_charge_std_time_call(self):
        start_record, end_record = self._setup_test(timedelta(
            minutes=5, seconds=10), 15)
        expected = Decimal("0.81")

        call_charge = self.controller._charge_call(
            start_record, end_record)

        self.assertEqual(call_charge, expected)

    def test_charge_reduced_time_call(self):
        start_record, end_record = self._setup_test(
            timedelta(minutes=5, seconds=10), 23, 15)
        expected = Decimal("0.36")

        call_charge = self.controller._charge_call(
            start_record, end_record)

        self.assertEqual(call_charge, expected)

    def test_charge_call_mixed_time(self):
        start_record, end_record = self._setup_test(
            timedelta(minutes=13, seconds=43), 21, 57, 13)
        expected = Decimal("0.54")

        call_charge = self.controller._charge_call(
            start_record, end_record)

        self.assertEqual(call_charge, expected)
