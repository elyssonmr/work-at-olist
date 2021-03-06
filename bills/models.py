from decimal import Decimal
from datetime import datetime, timedelta

from django.db import models, transaction
from django.utils import timezone


def cycle_date(billing_cycle=None):
    if not billing_cycle:
        now = timezone.now()
        billing_cycle = f"{now.month:02}/{now.year}"
    month, year = map(int, billing_cycle.split("/"))
    start_date = timezone.make_aware(
        datetime(day=1, month=month, year=year))
    end_date = timezone.make_aware(
        datetime(day=1, month=month + 1, year=year) - timedelta(days=1))
    
    return start_date, end_date

class CallRecord(models.Model):
    STARTING_CALL = "S"
    END_CALL = "E"
    CALL_TYPE = ((STARTING_CALL, "Starting Call"), (END_CALL, "End Call"))
    record_type = models.CharField(
        "Record Type", max_length=1, choices=CALL_TYPE, default=STARTING_CALL
    )
    timestamp = models.DateTimeField("Record Timestamp", default=timezone.now)
    call_id = models.IntegerField("Call ID")
    source = models.CharField(
        "Origin Phone Number", max_length=9, blank=False
    )
    destination = models.CharField(
        "Destination Phone Number", max_length=9, blank=False
    )
    bill = models.ForeignKey(
        "Bill", on_delete=models.DO_NOTHING, related_name="records", null=True)

    class Meta:
        unique_together = ("call_id", "record_type", "source")


class BillManager(models.Manager):

    def get_or_create(self, subscriber, period, standing_charge, minute_charge):
        try:
            bill = self.get(subscriber=subscriber, period=period)
        except Bill.DoesNotExist:
            bill = self.create_calculated_bill(
                subscriber, period, standing_charge, minute_charge)

        return bill

    @transaction.atomic
    def create_calculated_bill(self, subscriber, period, standing_charge, minute_charge):
        bill = self.create(
            subscriber=subscriber, period=period, standing_charge=standing_charge,
            minute_charge=minute_charge)
        CallRecord.objects.filter(
            source=subscriber, timestamp__range=cycle_date(period)
        ).update(bill=bill)
        bill.calculate()

        return bill


class Bill(models.Model):
    objects = BillManager()
    standing_charge = models.DecimalField("Standing Charge", max_digits=4, decimal_places=2)
    minute_charge = models.DecimalField("Minute Charge", max_digits=4, decimal_places=2)
    period = models.CharField("Period", max_length=7)
    subscriber = models.CharField(
        "Subscriber", max_length=9, blank=False
    )
    total_price = models.DecimalField("Total Price", max_digits=4, decimal_places=2, null=True)
    description = models.TextField("Description", blank=True)

    @property
    def is_calculated(self):
        return True if self.total_price else False

    def _charge_minutes(self, start_date, end_date):
        charged_minutes = 0
        current_time = start_date

        while current_time < end_date:
            current_time += timedelta(minutes=1)
            if current_time < end_date:
                if current_time.hour > 6 and current_time.hour < 22:
                    charged_minutes += 1

        return charged_minutes

    def _charge_call(self, start_record, end_record):
        billed_minutes = self._charge_minutes(
            start_record.timestamp, end_record.timestamp)
        return self.standing_charge + Decimal(billed_minutes * self.minute_charge)

    def _format_bill_records(self):
        start_records = {}
        end_records = {}
        records = []

        for record in self.records.all():
            if record.record_type == "S":
                start_records[record.call_id] = record
            else:
                end_records[record.call_id] = record
        for end_call_id in end_records:
            start_record = start_records.get(end_call_id, None)
            if not start_record:
                continue
            records.append((start_record, end_records[end_call_id]))
        return records

    def calculate(self):
        self.description = ""
        self.total_price = Decimal("0.0")
        for start_record, end_record in self._format_bill_records():
            charged_value = self._charge_call(start_record, end_record)
            self.description += (
                f"{start_record.timestamp}. From {start_record.source} to "
                f"{start_record.destination} billed: {charged_value:.2f}\n")
            self.total_price += charged_value
        self.save()


class Charge(models.Model):
    STANDING_CHARGE = "S"
    MINUTE_CHARGE = "M"
    CHARGE_TYPE = (
        (STANDING_CHARGE, "Standing Charge"),
        (MINUTE_CHARGE, "Minute Charge")
    )
    charge_type = models.CharField(
        "Charge Type", max_length=1, choices=CHARGE_TYPE,
        default=STANDING_CHARGE
    )

    value = models.DecimalField("Charge Value", max_digits=4, decimal_places=2)
