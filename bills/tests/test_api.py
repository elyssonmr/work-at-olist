import json

from decimal import Decimal
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from bills.models import CallRecord, Bill, Charge
from bills.tests import _setup_record


class CallRecordCreateAPITestCase(TestCase):
    def test_create_record(self):
        record_data = {
            "record_type": "E",
            "call_id": 1,
            "source": "12345678",
            "destination": "12345677",
            "timestamp": "2018-09-09T21:53:45.007978Z"
        }
        expected = record_data.copy()
        expected['id'] = 1

        response = self.client.post(
            '/api/callRecords',
            data=json.dumps(record_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertJSONEqual(response.content, expected)

    def test_create_invalid_record(self):
        record_data = {
            "record_type": "E",
            "call_id": 1,
            "source2": "12345678",
            "destination": "12345677"
        }
        expected = {
            "source": ['This field is required.']
        }

        response = self.client.post(
            '/api/callRecords',
            data=json.dumps(record_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, expected)

    def test_create_record_invalid_len_source(self):
        record_data = {
            "record_type": "E",
            "call_id": 1,
            "source": "12345",
            "destination": "12345677"
        }
        expected = {
            "source": ['Must be a phone number with 8 or 9 digits.']
        }

        response = self.client.post(
            '/api/callRecords',
            data=json.dumps(record_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, expected)

    def test_create_record_invalid_type_source(self):
        record_data = {
            "record_type": "E",
            "call_id": 1,
            "source": "abcdferg",
            "destination": "12345677"
        }
        expected = {
            "source": ['Must be digits.']
        }

        response = self.client.post(
            '/api/callRecords',
            data=json.dumps(record_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, expected)



class BillRetrieveTestCase(TestCase):
    def setUp(self):
        self.record_pair1 = _setup_record(
            timedelta(minutes=5, seconds=10), 15, call_id=1)
        self.record_pair2 = _setup_record(
            timedelta(minutes=3, seconds=10), 15, call_id=2)
        self.standing_charge = Charge.objects.create(
            charge_type="S", value=Decimal("0.35"))
        self.minute_charge = Charge.objects.create(
            charge_type="M", value=Decimal("0.09"))

    def test_get_bill(self):
        now = timezone.now()
        cycle = f"{now.year}/{now.month:02}"
        url = f"/api/bills/{cycle}/12345678"

        response = self.client.get(url, content_type='application/json')

        self.assertEqual(response.status_code, 200)

        bill = json.loads(response.content)
        self.assertEqual(bill["id"], 1)
        self.assertEqual(bill["total_price"], str(Decimal("1.42")))
        self.assertEqual(bill["period"], f"{now.month:02}/{now.year}")
