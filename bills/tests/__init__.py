from datetime import timedelta

from django.utils import timezone

from bills.models import CallRecord, Bill, cycle_date

def _setup_record(call_duration, start_hour=0, start_minute=0,
                  start_second=0, call_id=1, outdated=False):
    call_time = timezone.now()
    if outdated:
        call_time = call_time + timedelta(days=30)
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
