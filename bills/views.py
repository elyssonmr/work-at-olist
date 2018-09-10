from rest_framework.generics import CreateAPIView, RetrieveAPIView

from bills.serializers import CallRecordModelSerializer, BillModelSerializer

from bills.models import Bill, Charge

class CallRecordCreateAPIView(CreateAPIView):
    serializer_class = CallRecordModelSerializer

    def get_extra_actions(self):
        return []


class BillRetrieverView(RetrieveAPIView):
    serializer_class = BillModelSerializer

    def get_object(self):
        subscriber = self.kwargs['source']
        month = self.kwargs['month']
        year = self.kwargs['year']
        print(subscriber, month, year)
        standing_charge = Charge.objects.get(charge_type='S').value
        minute_charge = Charge.objects.get(charge_type='M').value

        period = f"{month}/{year}"

        return Bill.objects.get_or_create(
            subscriber, period, standing_charge, minute_charge
        )
