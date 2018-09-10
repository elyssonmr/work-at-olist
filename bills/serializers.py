from rest_framework.serializers import ModelSerializer

from bills.models import CallRecord, Bill

class CallRecordModelSerializer(ModelSerializer):
    class Meta:
        model = CallRecord
        fields = ('id', 'record_type', 'timestamp', 'call_id', 'source',
                  'destination')


class BillModelSerializer(ModelSerializer):
    class Meta:
        model = Bill
        fields = ('id', 'standing_charge', 'minute_charge', 'period',
                  'subscriber', 'total_price', 'description')
