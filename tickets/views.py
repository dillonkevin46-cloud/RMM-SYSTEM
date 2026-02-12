from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Ticket, TicketCategory
from rmm.models import Agent
from django.contrib.auth.models import User
from django.utils import timezone

@login_required
def ticket_list(request):
    # Filter: Show Open tickets first
    tickets = Ticket.objects.all().order_by('status', '-created_at')
    
    context = {
        'tickets': tickets,
        'stats_open': tickets.filter(status='Open').count(),
        'stats_progress': tickets.filter(status='In Progress').count(),
    }
    
    # If HTMX request, just return the table rows
    if request.htmx:
        return render(request, 'tickets/partials/ticket_table.html', context)
        
    return render(request, 'tickets/ticket_dashboard.html', context)

@login_required
def ticket_create(request):
    if request.method == "POST":
        # Process the form
        Ticket.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            priority=request.POST.get('priority'),
            agent_id=request.POST.get('agent_id') if request.POST.get('agent_id') else None,
            created_by=request.user.username
        )
        return redirect('ticket_list')

    # Show the form
    context = {
        'agents': Agent.objects.all(),
        'priorities': ['Low', 'Medium', 'High', 'Critical']
    }
    return render(request, 'tickets/ticket_form.html', context)

# API for Agent (No Login Required)
@csrf_exempt
def api_create_ticket(request):
    if request.method == 'POST':
        try:
            agent_id = request.POST.get('agent_id')
            title = request.POST.get('title')
            description = request.POST.get('description')
            
            agent = Agent.objects.filter(agent_id=agent_id).first()
            
            ticket = Ticket.objects.create(
                title=title,
                description=description,
                agent=agent,
                priority='Medium',
                created_by=f"User on {agent.hostname if agent else 'Unknown'}"
            )
            
            return JsonResponse({"status": "success", "ticket_id": ticket.id})
            
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error"}, status=400)