from django.db import models
from django.contrib.auth.models import User

# 1. The Template (e.g., "Morning Checks")
class Checklist(models.Model):
    name = models.CharField(max_length=100) # e.g. "Morning Server Check"
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

# 2. The Items in the list (e.g., "Check Backups")
class ChecklistItem(models.Model):
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE)
    text = models.CharField(max_length=200) # 
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return self.text

# 3. The Actual Daily Report (The history)
class Submission(models.Model):
    checklist = models.ForeignKey(Checklist, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.checklist.name} - {self.created_at.strftime('%Y-%m-%d')}"

# 4. The Result of each item (Pass/Fail + Notes)
class SubmissionItem(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE)
    item_text = models.CharField(max_length=200) # Copy text in case template changes
    status = models.BooleanField(default=True) # True = Working, False = Issue [cite: 50]
    notes = models.CharField(max_length=255, blank=True) #