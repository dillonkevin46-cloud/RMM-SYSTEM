from django.db import models
from django.utils import timezone

class DeviceGroup(models.Model):
    """
    Categorizes devices (e.g., 'Office PCs', 'Servers', 'Remote Laptops')
    """
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Agent(models.Model):
    """
    Represents a single computer or device managed by the RMM system.
    """
    # --- Identification ---
    hostname = models.CharField(max_length=255)
    agent_id = models.CharField(max_length=100, unique=True)
    serial_number = models.CharField(max_length=100, blank=True)
    mac_address = models.CharField(max_length=50, blank=True)
    
    # --- Categories & Sorting ---
    group = models.ForeignKey(DeviceGroup, on_delete=models.SET_NULL, null=True, blank=True)
    is_favorite = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    # --- Hardware Details ---
    operating_system = models.CharField(max_length=255, blank=True)
    cpu_model = models.CharField(max_length=255, blank=True)
    ram_total = models.CharField(max_length=50, blank=True)
    
    # --- Network Details ---
    public_ip = models.CharField(max_length=50, blank=True, null=True)
    private_ip = models.CharField(max_length=50, blank=True, null=True)
    
    # --- Status Monitoring ---
    last_seen = models.DateTimeField(default=timezone.now)
    is_online = models.BooleanField(default=False)
    last_login_user = models.CharField(max_length=100, blank=True)
    
    # --- Monitoring Configuration ---
    is_crucial = models.BooleanField(default=False)
    custom_dns = models.CharField(max_length=50, default="8.8.8.8")
    alert_email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.hostname} ({self.private_ip})"

class PerformanceLog(models.Model):
    """
    Stores historical performance data for generating graphs.
    """
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Metrics recorded by the Agent
    cpu_usage = models.FloatField(default=0.0) # Percentage
    ram_usage = models.FloatField(default=0.0) # Percentage
    disk_usage = models.FloatField(default=0.0) # <--- NEW FIELD
    latency_ms = models.FloatField(default=0.0) # Milliseconds (Ping)
    
    def __str__(self):
        return f"{self.agent.hostname} @ {self.timestamp.strftime('%H:%M:%S')}"