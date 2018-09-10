from rest_framework import serializers

from bills.models import CallRecord, Bill

def _validate_phone_number(number):
        if len(number) < 8 or len(number) > 9:
            raise serializers.ValidationError("Must be a phone number with 8 or 9 digits.")

        if not number.isdigit():
            raise serializers.ValidationError("Must be digits.")

        return number


class CallRecordModelSerializer(serializers.ModelSerializer):
    source = serializers.CharField(validators=[_validate_phone_number])
    destination = serializers.CharField(validators=[_validate_phone_number])

    class Meta:
        model = CallRecord
        fields = ('id', 'record_type', 'timestamp', 'call_id', 'source',
                  'destination')


class BillModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bill
        fields = ('id', 'standing_charge', 'minute_charge', 'period',
                  'subscriber', 'total_price', 'description')
