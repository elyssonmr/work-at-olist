"""
1. Standard time call - between 6h00 and 22h00 (excluding):

    Standing charge: R$ 0,36 (fixed charges that are used to pay for the cost of 
the connection);
    Call charge/minute: R$ 0,09 (there is no fractioned charge. The charge applies
to each completed 60 seconds cycle).

2. Reduced tariff time call - between 22h00 and 6h00 (excluding):

    Standing charge: R$ 0,36
    Call charge/minute: R$ 0,00 (hooray!)

It's important to notice that the price rules can change from time to 
time, but an already calculated call price can not change.

Examples
For a call started at 21:57:13 and finished at 22:10:56 we have:

    Standing charge: R$ 0,36
    Call charge:
        minutes between 21:57:13 and 22:00 = 2
        price: 2 * R$ 0,09 = R$ 0,18
        Total: R$ 0,18 + R$ 0,36 = R$ 0,54

"""
from decimal import Decimal
from datetime import datetime, timedelta
from math import ceil

STANDING_CHARGE = Decimal("0.36")
STANDARD_CHARGE = Decimal("0.09")



class BillCalculator:
    def __init__(self, records, standing_charge, minute_value):
        self._records = records
        self._standing_charge = standing_charge
        self._minute_value = minute_value

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

        return STANDING_CHARGE + Decimal(billed_minutes * STANDARD_CHARGE)

    def calculate_bill(self):
        bill_records = []
        for start_record, end_record in self._records:
            charged_value = self._charge_call(start_record, end_record)
            bill_records.append({
                "value": charged_value,
                "start_record": start_record,
                "end_record": end_record
            })

        return bill_records
