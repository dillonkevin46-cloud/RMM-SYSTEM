from django.contrib import admin
from .models import DocumentCategory, KnowledgeDocument, ManualAsset

admin.site.register(DocumentCategory)
admin.site.register(KnowledgeDocument)
admin.site.register(ManualAsset)