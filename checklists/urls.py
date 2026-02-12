from django.urls import path
from . import views

urlpatterns = [
    path('', views.checklists_dashboard, name='checklists_dashboard'),
    path('perform/<int:checklist_id>/', views.perform_checklist, name='perform_checklist'),
    path('onboarding/', views.onboarding_form, name='onboarding_form'),
]