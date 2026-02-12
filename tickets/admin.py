from django.contrib import admin
from .models import Ticket, TicketCategory, TicketComment

class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'status', 'priority', 'agent', 'created_at')
    list_filter = ('status', 'priority')

admin.site.register(Ticket, TicketAdmin)
admin.site.register(TicketCategory)
admin.site.register(TicketComment)