from django.urls import path
from . import views

urlpatterns = [
    path('api/checkin/', views.check_in, name='agent_checkin'),
    path('', views.dashboard, name='dashboard'), # The main dashboard
    path('api/checkin/', views.check_in, name='agent_checkin'),
    path('remote/<str:agent_id>/', views.remote_view, name='remote_view'),
    path('monitoring/', views.monitoring_dashboard, name='monitoring'),
]