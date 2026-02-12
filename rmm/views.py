from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required # Import the decorator
from django.utils import timezone
from datetime import timedelta
import json

# Import your models
from .models import Agent, PerformanceLog

# --- DASHBOARD (Protected) ---
@login_required
def dashboard(request):
    # 1. Define the timeout (e.g., 30 seconds)
    timeout_threshold = timezone.now() - timedelta(seconds=30)
    
    # 2. Mark agents as offline if they haven't checked in
    offline_agents = Agent.objects.filter(last_seen__lt=timeout_threshold, is_online=True)
    offline_agents.update(is_online=False)
    
    # 3. Fetch all agents
    agents = Agent.objects.all().order_by('-is_online', 'hostname')
    
    # 4. Calculate stats
    total_agents = agents.count()
    online_count = agents.filter(is_online=True).count()
    offline_count = total_agents - online_count
    
    context = {
        'agents': agents,
        'total': total_agents,
        'online': online_count,
        'offline': offline_count,
    }
    
    # HTMX Partial Update
    if request.htmx:
        return render(request, 'rmm/partials/agent_list.html', context)
        
    return render(request, 'rmm/dashboard.html', context)

# --- REMOTE DESKTOP (Protected) ---
@login_required
def remote_view(request, agent_id):
    return render(request, 'rmm/remote_view.html', {'agent_id': agent_id})

# --- MONITORING (Protected) ---
@login_required
def monitoring_dashboard(request):
    agents = Agent.objects.all()
    
    selected_agent_id = request.GET.get('agent_id')
    selected_agent = None
    labels = []
    data_cpu = []
    data_ram = []
    data_latency = []
    
    if selected_agent_id:
        selected_agent = get_object_or_404(Agent, id=selected_agent_id)
        # Get last 20 logs
        logs = PerformanceLog.objects.filter(agent=selected_agent).order_by('-timestamp')[:20]
        # Reverse them so the graph goes left-to-right
        logs = reversed(logs)
        
        for log in logs:
            labels.append(log.timestamp.strftime("%H:%M:%S"))
            data_cpu.append(log.cpu_usage)
            data_ram.append(log.ram_usage)
            data_latency.append(log.latency_ms)

    context = {
        'agents': agents,
        'selected_agent': selected_agent,
        'labels': labels,
        'data_cpu': data_cpu,
        'data_ram': data_ram,
        'data_latency': data_latency,
    }
    return render(request, 'rmm/monitoring.html', context)

# --- API: AGENT CHECK-IN (NOT PROTECTED) ---
# This is accessed by the Agent script, not a human, so no login required.
@csrf_exempt 
def check_in(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Find or Create Agent
            agent, created = Agent.objects.get_or_create(
                agent_id=data.get('agent_id'),
                defaults={'hostname': data.get('hostname')}
            )
            
            # Update Basic Info
            agent.hostname = data.get('hostname')
            agent.operating_system = data.get('operating_system')
            agent.cpu_model = data.get('cpu_model')
            agent.ram_total = data.get('ram_total')
            agent.public_ip = data.get('public_ip')
            agent.private_ip = data.get('private_ip')
            agent.mac_address = data.get('mac_address')
            agent.last_login_user = data.get('last_login_user')
            
            # Update Status
            agent.last_seen = timezone.now()
            agent.is_online = True
            agent.save()
            
            # --- Save History for Graphs ---
            if 'cpu_percent' in data:
                PerformanceLog.objects.create(
                    agent=agent,
                    cpu_usage=data.get('cpu_percent', 0),
                    ram_usage=data.get('ram_percent', 0),
                    latency_ms=data.get('latency_ms', 0)
                )
            
            return JsonResponse({"status": "success"})
            
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    return JsonResponse({"status": "error", "message": "POST required"}, status=400)