from django.db import models
from rmm.models import DeviceGroup # Link to existing groups

class DocumentCategory(models.Model):
    name = models.CharField(max_length=100) # e.g., "SOP", "Invoice", "Guide"
    
    def __str__(self):
        return self.name

class KnowledgeDocument(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(DocumentCategory, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    
    # The actual file upload
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

# [cite: 37] - Manual Asset Registry
class ManualAsset(models.Model):
    name = models.CharField(max_length=200) # e.g. "Office Printer"
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    serial_number = models.CharField(max_length=100, blank=True)
    group = models.ForeignKey(DeviceGroup, on_delete=models.SET_NULL, null=True)
    purchase_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return self.name