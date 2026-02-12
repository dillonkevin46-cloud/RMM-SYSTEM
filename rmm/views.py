from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
import json

# Import your models
from .models import Agent, PerformanceLog

# --- DASHBOARD (Protected) ---
@login_required
def dashboard(request):
    timeout_threshold = timezone.now() - timedelta(seconds=30)
    
    offline_agents = Agent.objects.filter(last_seen__lt=timeout_threshold, is_online=True)
    offline_agents.update(is_online=False)
    
    agents = Agent.objects.all().order_by('-is_online', 'hostname')
    
    context = {
        'agents': agents,
        'total': agents.count(),
        'online': agents.filter(is_online=True).count(),
        'offline': agents.filter(is_online=False).count(),
    }
    
    if request.htmx:
        return render(request, 'rmm/partials/agent_list.html', context)
        
    return render(request, 'rmm/dashboard.html', context)

# --- REMOTE DESKTOP (Protected) ---
@login_required
def remote_view(request, agent_id):
    return render(request, 'rmm/remote_view.html', {'agent_id': agent_id})

# --- TERMINAL (Protected) ---
@login_required
def terminal_view(request, agent_id):
    # Pass the full agent object so we can link back to monitoring
    agent = get_object_or_404(Agent, agent_id=agent_id)
    return render(request, 'rmm/terminal.html', {'agent_id': agent_id, 'agent': agent})

# --- MONITORING (Protected) ---
@login_required
def monitoring_dashboard(request):
    agents = Agent.objects.all()
    
    selected_agent_id = request.GET.get('agent_id')
    selected_agent = None
    labels = []
    data_cpu = []
    data_ram = []
    data_disk = [] # <--- NEW LIST
    data_latency = []
    
    if selected_agent_id:
        selected_agent = get_object_or_404(Agent, id=selected_agent_id)
        # Get last 20 logs
        logs = PerformanceLog.objects.filter(agent=selected_agent).order_by('-timestamp')[:20]
        logs = reversed(logs)
        
        for log in logs:
            labels.append(log.timestamp.strftime("%H:%M:%S"))
            data_cpu.append(log.cpu_usage)
            data_ram.append(log.ram_usage)
            data_disk.append(log.disk_usage) # <--- ADD THIS
            data_latency.append(log.latency_ms)

    context = {
        'agents': agents,
        'selected_agent': selected_agent,
        'labels': labels,
        'data_cpu': data_cpu,
        'data_ram': data_ram,
        'data_disk': data_disk, # <--- PASS TO TEMPLATE
        'data_latency': data_latency,
    }
    return render(request, 'rmm/monitoring.html', context)

# --- API: AGENT CHECK-IN (NOT PROTECTED) ---
@csrf_exempt 
def check_in(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            agent, created = Agent.objects.get_or_create(
                agent_id=data.get('agent_id'),
                defaults={'hostname': data.get('hostname')}
            )
            
            agent.hostname = data.get('hostname')
            agent.operating_system = data.get('operating_system')
            agent.cpu_model = data.get('cpu_model')
            agent.ram_total = data.get('ram_total')
            agent.public_ip = data.get('public_ip')
            agent.private_ip = data.get('private_ip')
            agent.mac_address = data.get('mac_address')
            agent.last_login_user = data.get('last_login_user')
            
            agent.last_seen = timezone.now()
            agent.is_online = True
            agent.save()
            
            if 'cpu_percent' in data:
                PerformanceLog.objects.create(
                    agent=agent,
                    cpu_usage=data.get('cpu_percent', 0),
                    ram_usage=data.get('ram_percent', 0),
                    disk_usage=data.get('disk_percent', 0), # <--- SAVE THIS
                    latency_ms=data.get('latency_ms', 0)
                )
            
            return JsonResponse({"status": "success"})
            
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    return JsonResponse({"status": "error", "message": "POST required"}, status=400)