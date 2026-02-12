from django.contrib import admin
from .models import Agent, DeviceGroup, PerformanceLog

# Customize how the Agent list looks
class AgentAdmin(admin.ModelAdmin):
    list_display = ('hostname', 'private_ip', 'is_online', 'last_seen', 'group')
    list_filter = ('is_online', 'group', 'operating_system')
    search_fields = ('hostname', 'private_ip', 'agent_id')

admin.site.register(Agent, AgentAdmin)
admin.site.register(DeviceGroup)
admin.site.register(PerformanceLog)