from datetime import datetime, timedelta

from django.db import models
from django.utils import timezone


def cycle_date(billing_cycle):
    if not billing_cycle:
        now = timezone.now()
        billing_cycle = f"{now.month:02}/{now.year}"
    month, year = map(int, billing_cycle.split("/"))
    start_date = timezone.make_aware(
        datetime(day=1, month=month, year=year))
    end_date = timezone.make_aware(
        datetime(day=1, month=month + 1, year=year) - timedelta(days=1))
    
    return start_date, end_date


class CallRecordManager(models.Manager):
    def get_bill_records(self, subscriber, billing_cycle=None):
        call_records = self.filter(
            source=subscriber, timestamp__range=cycle_date(billing_cycle)
        )
        start_calls = {}
        end_calls = {}
        for record in call_records:
            if record.record_type == "S":
                start_calls[record.call_id] = record
            else:
                end_calls[record.call_id] = record
        records = []
        for end_call_id in end_calls:
            start_record = start_calls.get(end_call_id, None)
            if not start_record:
                continue
            records.append((start_record, end_calls[end_call_id]))
        return records


class CallRecord(models.Model):
    objects = CallRecordManager()
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

    class Meta:
        unique_together = ("call_id", "record_type", "source")
