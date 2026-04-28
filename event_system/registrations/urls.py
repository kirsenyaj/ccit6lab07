from django.urls import path
from .views import (
    register_patient,
    add_to_queue,
    request_lab_test,
    get_queue,
)
 
urlpatterns = [
    path('patients/', register_patient),
    path('queue/', add_to_queue),
    path('queue/list/', get_queue),
    path('lab-tests/', request_lab_test),
]
