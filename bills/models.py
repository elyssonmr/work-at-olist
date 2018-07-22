from django.db import models

# Create your models here.


class CallRecord(models.Model):
    STARTING_CALL = "S"
    END_CALL = "E"
    CALL_TYPE = ((STARTING_CALL, "Starting Call"), (END_CALL, "End Call"))
    record_type = models.CharField(
        "Record Type", max_length=1, choices=CALL_TYPE, default=STARTING_CALL
    )
    timestamp = models.DateTimeField("Record Timestamp", auto_now=True)
    call_id = models.UUIDField("Call ID")
    source = models.CharField(
        "Origin Phone Number", max_length=9, blank=False
    )
    destination = models.CharField(
        "Destination Phone Number", max_length=9, blank=False
    )

    class Meta:
        unique_together = ("call_id", "record_type", "source")
