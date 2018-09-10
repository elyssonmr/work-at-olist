from django.urls import re_path as path

from bills.views import CallRecordCreateAPIView, BillRetrieverView

urlpatterns = [
    path(r'callRecords/?$', CallRecordCreateAPIView.as_view(),
         name='call_record'),
    path(r'bills/(?P<year>\d{4})/(?P<month>\d{2})/(?P<source>\d{8,9})/?$',
         BillRetrieverView.as_view(), name='bill'),
]
