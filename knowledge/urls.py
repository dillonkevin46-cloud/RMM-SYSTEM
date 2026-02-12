from django.urls import path
from . import views

urlpatterns = [
    path('', views.kb_dashboard, name='kb_dashboard'),
    path('upload/', views.upload_document, name='upload_document'),
    path('add_asset/', views.add_manual_asset, name='add_manual_asset'),
]