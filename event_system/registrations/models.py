from django.db import models
import django.utils.timezone
 
 
class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    contact_number = models.CharField(max_length=20)
    barangay = models.CharField(max_length=100, default="Not Specified")
    created_at = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
 
 
class Staff(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=50)
 
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"
 
 
class Queue(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    service_area = models.CharField(max_length=50)
    queue_number = models.IntegerField()
    STATUS_CHOICES = [
        ('Waiting', 'Waiting'),
        ('In Progress', 'In Progress'),
        ('Done', 'Done'),
        ('Cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Waiting')
    check_in_time = models.DateTimeField(auto_now_add=True)
    queue_date = models.DateField(default=django.utils.timezone.now)
 
    def __str__(self):
        return f"#{self.queue_number} - {self.service_area}"
 
 
class LabTest(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(Staff, on_delete=models.CASCADE)
    test_type = models.CharField(max_length=100)
    result = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, default='Pending')
    request_date = models.DateTimeField(auto_now_add=True)
 
    def __str__(self):
        return f"{self.test_type} - {self.patient}"

