from django.urls import path
from . import views

urlpatterns = [
    path('send_test_email/<int:message_id>/',
         views.send_test_email, name='send_test_email'),
]
