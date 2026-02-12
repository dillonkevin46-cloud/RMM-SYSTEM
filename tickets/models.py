from django.db import models
from django.contrib.auth.models import User
from rmm.models import Agent # Link tickets to devices

class TicketCategory(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class Ticket(models.Model):
    STATUS_CHOICES = (
        ('Open', 'Open'),
        ('In Progress', 'In Progress'),
        ('Waiting on Client', 'Waiting on Client'),
        ('Closed', 'Closed'),
    )
    
    PRIORITY_CHOICES = (
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Critical', 'Critical'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Classification
    category = models.ForeignKey(TicketCategory, on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    
    # Relationships
    agent = models.ForeignKey(Agent, on_delete=models.SET_NULL, null=True, blank=True) # Which PC is broken?
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True) # Which staff member?
    created_by = models.CharField(max_length=100, default="System") # Name of client or user
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    # Time Tracking (Requirement 20)
    time_spent_minutes = models.IntegerField(default=0)

    def __str__(self):
        return f"#{self.id} - {self.title}"

class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    text = models.TextField()
    is_private = models.BooleanField(default=False) # Internal notes vs Client replies
    created_at = models.DateTimeField(auto_now_add=True)