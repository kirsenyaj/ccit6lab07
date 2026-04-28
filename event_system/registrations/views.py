from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import datetime
from .models import Patient, Staff, Queue, LabTest
 
 
# Feature 1: Register Patient
@api_view(['POST'])
def register_patient(request):
    first_name = request.data.get('first_name')
    last_name = request.data.get('last_name')
    date_of_birth = request.data.get('date_of_birth')
    gender = request.data.get('gender')
    contact_number = request.data.get('contact_number')
 
    # DFD: Validate
    if not all([first_name, last_name, date_of_birth, gender, contact_number]):
        return Response({"status": "error", "message": "Missing required fields"})
 
    # DFD: Save Patient
    patient = Patient.objects.create(
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        gender=gender,
        contact_number=contact_number,
    )
 
    return Response({
        "status": "success",
        "message": "Patient registered successfully",
        "patient_id": patient.id,
    })
 
 
# Feature 2: Add Patient to Service Queue
@api_view(['POST'])
def add_to_queue(request):
    patient_id = request.data.get('patient_id')
    service_area = request.data.get('service_area')
 
    # DFD: Validate input
    if not patient_id or not service_area:
        return Response({"status": "error", "message": "Missing data"})
 
    # DFD: Validate schedule (clinic operating hours)
    now = datetime.now()
    weekday = now.weekday()  # 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri
    hour = now.hour
 
    if service_area in ['Consultation', 'Laboratory']:
        if weekday not in [1, 2, 3] or hour < 9 or hour >= 11:

            return Response({
                "status": "error",
                "message": "Service available only Tue-Thu, 9AM-11AM",
            })
    elif service_area == 'Animal Bite Treatment':
        if weekday not in [0, 1, 2, 3, 4] or hour < 9 or hour >= 18:

            return Response({
                "status": "error",
                "message": "Service available only Mon-Fri, 9AM-6PM",
            })
 
    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return Response({"status": "error", "message": "Invalid patient"})
 
    # DFD: Generate queue number
    last = Queue.objects.filter(
        service_area=service_area,
        queue_date=now.date(),
    ).order_by('-queue_number').first()
    next_number = (last.queue_number + 1) if last else 1
 
    # DFD: Save Queue
    entry = Queue.objects.create(
        patient=patient,
        service_area=service_area,
        queue_number=next_number,
    )
 
    return Response({
        "status": "success",
        "message": "Patient added to queue",
        "queue_number": entry.queue_number,
        "service_area": entry.service_area,
    })
 
 
# Feature 3: Request Laboratory Test
@api_view(['POST'])
def request_lab_test(request):
    patient_id = request.data.get('patient_id')
    requested_by = request.data.get('requested_by')
    test_type = request.data.get('test_type')
 
    # DFD: Validate
    if not all([patient_id, requested_by, test_type]):
        return Response({"status": "error", "message": "Missing data"})
 
    try:
        patient = Patient.objects.get(id=patient_id)
        staff = Staff.objects.get(id=requested_by)
    except (Patient.DoesNotExist, Staff.DoesNotExist):
        return Response({"status": "error", "message": "Invalid patient or staff"})
 
    # DFD: Save Lab Test
    lab_test = LabTest.objects.create(
        patient=patient,
        requested_by=staff,
        test_type=test_type,
    )
 
    return Response({
        "status": "success",
        "message": "Lab test request created",
        "lab_test_id": lab_test.id,
    })
 
 
# Supporting endpoint: View Queue
@api_view(['GET'])
def get_queue(request):
    entries = Queue.objects.filter(queue_date=datetime.now().date())
    data = [{
        "queue_id": q.id,
        "patient": str(q.patient),
        "service_area": q.service_area,
        "queue_number": q.queue_number,
        "status": q.status,
    } for q in entries]
    return Response(data)
