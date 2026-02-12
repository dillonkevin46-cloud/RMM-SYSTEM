from django.contrib import admin
from .models import Checklist, ChecklistItem, Submission, SubmissionItem

class ItemInline(admin.TabularInline):
    model = ChecklistItem

class ChecklistAdmin(admin.ModelAdmin):
    inlines = [ItemInline] # Allows adding items directly inside the Checklist page

class SubmissionItemInline(admin.TabularInline):
    model = SubmissionItem
    readonly_fields = ('item_text', 'status', 'notes')

class SubmissionAdmin(admin.ModelAdmin):
    inlines = [SubmissionItemInline]
    readonly_fields = ('created_at', 'user', 'checklist')

admin.site.register(Checklist, ChecklistAdmin)
admin.site.register(Submission, SubmissionAdmin)