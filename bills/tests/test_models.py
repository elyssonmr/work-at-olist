from decimal import Decimal
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone


from bills.models import CallRecord, Bill, cycle_date
from bills.tests import _setup_record


class CycleDateTestCase(TestCase):
    def test_cycle_date_current_month(self):
        now = timezone.now()
        billing_cycle = f"{now.month:02}/{now.year}"
        start_date, end_date = cycle_date(billing_cycle)

        self.assertGreaterEqual(now, start_date)
        self.assertLessEqual(now, end_date)
    
    def test_cycle_date_next_month(self):
        next_month = timezone.now() + timedelta(days=30)
        billing_cycle = f"{next_month.month:02}/{next_month.year}"
        start_date, end_date = cycle_date(billing_cycle)

        self.assertGreaterEqual(next_month, start_date)
        self.assertLessEqual(next_month, end_date)
    
    def test_cycle_date_no_args(self):
        now = timezone.now()

        start_date, end_date = cycle_date()

        self.assertGreaterEqual(now, start_date)
        self.assertLessEqual(now, end_date)

class BillCreateTestCase(TestCase):
    def test_create_bill(self):
        subscriber = "12345678"
        start_record, end_record = _setup_record(
            timedelta(minutes=5, seconds=10), 15, call_id=1)
        standing_charge = Decimal("0.36")
        minute_charge = Decimal("0.09")
        now = timezone.now()
        period = f"{now.month:02}/{now.year}"

        bill = Bill.objects.get_or_create(
            subscriber, period, standing_charge, minute_charge)

        self.assertEqual(bill.pk, 1)
        self.assertEqual([start_record, end_record], list(bill.records.all()))


class BillCalculateBillTestCase(TestCase):
    def setUp(self):
        now = timezone.now()
        call_id = 1
        self.records1 = _setup_record(
            timedelta(minutes=5, seconds=10), 15, call_id=call_id)
        call_id += 1
        _setup_record(
            timedelta(minutes=10, seconds=50), 21, 57, 13, call_id=call_id)
        call_id += 1
        _setup_record(
            timedelta(minutes=10, seconds=50), 21, 57, 13,
            call_id=call_id, outdated=True)
        standing_charge = Decimal("0.36")
        minute_charge = Decimal("0.09")
        period = f"{now.month:02}/{now.year}"
        self.bill = Bill.objects.create_calculated_bill(
            "12345678", period, standing_charge, minute_charge
        )

    def test_calculate_bill(self):
        expected_total = Decimal("1.35")
        self.bill.calculate()

        self.assertTrue(self.bill.is_calculated)
        self.assertEqual(self.bill.total_price, expected_total)

    def test_calculate_without_start_record(self):
        self.records1[0].delete()
        self.bill.calculate()

        expected_total = Decimal("0.54")

        self.assertEqual(self.bill.total_price, expected_total)
