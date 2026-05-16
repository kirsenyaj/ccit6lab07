from django.contrib import admin
from .models import Patient, Staff, Queue, LabTest
from django.utils.translation import gettext_lazy as _

class PatientAdmin(admin.ModelAdmin):
    list_display = ('formatted_id', 'first_name', 'last_name', 'contact_number', 'created_at')
    search_fields = ('first_name', 'last_name', 'id')
    
    def formatted_id(self, obj):
        return f"PAT-{obj.id:04d}"
    formatted_id.short_description = 'Patient ID'

class ExactDateFilter(admin.SimpleListFilter):
    title = _('exact queue date')
    parameter_name = 'exact_date'

    def lookups(self, request, model_admin):
        # Get all unique dates from the queue
        dates = model_admin.model.objects.values_list('queue_date', flat=True).distinct().order_by('-queue_date')
        return [(d, d.strftime('%B %d, %Y')) for d in dates if d]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(queue_date=self.value())
        return queryset

class QueueAdmin(admin.ModelAdmin):
    list_display = ('formatted_queue', 'patient_id_formatted', 'patient', 'service_area', 'queue_date', 'status')
    list_filter = ('service_area', ExactDateFilter, 'status')
    date_hierarchy = 'queue_date'
    
    def formatted_queue(self, obj):
        prefix = ""
        if obj.service_area == 'Consultation':
            prefix = "CON-"
        elif obj.service_area == 'Laboratory':
            prefix = "LAB-"
        elif obj.service_area == 'Animal Bite Treatment':
            prefix = "ABT-"
        return f"{prefix}{obj.queue_number:03d}"
    formatted_queue.short_description = 'Queue Number'

    def patient_id_formatted(self, obj):
        return f"PAT-{obj.patient.id:04d}"
    patient_id_formatted.short_description = 'Patient ID'

admin.site.register(Patient, PatientAdmin)
admin.site.register(Staff)
admin.site.register(Queue, QueueAdmin)
admin.site.register(LabTest)
