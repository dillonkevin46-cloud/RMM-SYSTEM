# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Add this line for built-in auth (login/logout)
    path('accounts/', include('django.contrib.auth.urls')), 
    
    path('rmm/', include('rmm.urls')),
    path('tickets/', include('tickets.urls')),
    path('kb/', include('knowledge.urls')),
    path('forms/', include('checklists.urls')),
]