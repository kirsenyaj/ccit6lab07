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
 
    formatted_patient_id = f"PAT-{patient.id:04d}"

    return Response({
        "status": "success",
        "message": "Patient registered successfully",
        "patient_id": formatted_patient_id,
    })
 
 
# Feature 2: Add Patient to Service Queue
@api_view(['POST'])
def add_to_queue(request):
    patient_id = request.data.get('patient_id')
    service_area = request.data.get('service_area')
    queue_date_str = request.data.get('queue_date')
 
    # DFD: Validate input
    if not patient_id or not service_area:
        return Response({"status": "error", "message": "Missing data"})
  
    if queue_date_str:
        try:
            queue_date = datetime.strptime(queue_date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({"status": "error", "message": "Invalid date format"})
    else:
        queue_date = datetime.now().date()
 
    # DFD: Validate schedule (based on selected date's day of week)
    weekday = queue_date.weekday()  # 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
 
    if service_area in ['Consultation', 'Laboratory']:
        if weekday not in [1, 2, 3]:
            return Response({
                "status": "error",
                "message": "This service is only available on Tuesdays, Wednesdays, and Thursdays between 9AM and 11AM."
            })
    elif service_area == 'Animal Bite Treatment':
        if weekday not in [0, 1, 2, 3, 4]:
            return Response({
                "status": "error",
                "message": "This service is only available from Monday to Friday between 9AM and 3PM."
            })
 
    try:
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        return Response({"status": "error", "message": "Invalid patient"})
 
    # DFD: Generate queue number
    last = Queue.objects.filter(
        service_area=service_area,
        queue_date=queue_date,
    ).order_by('-queue_number').first()
    next_number = (last.queue_number + 1) if last else 1
 
    # Check Daily Limit
    DAILY_LIMIT = 50  # Admin can change this number to adjust the maximum patients per day
    if next_number > DAILY_LIMIT:
        return Response({
            "status": "error", 
            "message": f"Sorry, the daily limit of {DAILY_LIMIT} appointments for {service_area} on this date has been reached. Please select another date."
        })
 
    # DFD: Save Queue
    entry = Queue.objects.create(
        patient=patient,
        service_area=service_area,
        queue_number=next_number,
        queue_date=queue_date,
    )
 
    # Format queue number with service prefix
    prefix = ""
    if service_area == 'Consultation':
        prefix = "CON-"
    elif service_area == 'Laboratory':
        prefix = "LAB-"
    elif service_area == 'Animal Bite Treatment':
        prefix = "ABT-"

    formatted_number = f"{prefix}{entry.queue_number:03d}"

    return Response({
        "status": "success",
        "message": "Patient added to queue",
        "queue_number": formatted_number,
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
