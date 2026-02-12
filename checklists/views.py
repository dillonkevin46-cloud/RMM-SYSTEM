from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Checklist, Submission, SubmissionItem
from tickets.models import Ticket

@login_required
def checklists_dashboard(request):
    checklists = Checklist.objects.all()
    history = Submission.objects.all().order_by('-created_at')[:10]
    return render(request, 'checklists/dashboard.html', {'checklists': checklists, 'history': history})

@login_required
def perform_checklist(request, checklist_id):
    checklist = get_object_or_404(Checklist, id=checklist_id)
    
    if request.method == "POST":
        sub = Submission.objects.create(checklist=checklist, user=request.user)
        
        items = checklist.checklistitem_set.all()
        for item in items:
            status = request.POST.get(f"status_{item.id}") == "pass"
            notes = request.POST.get(f"notes_{item.id}")
            
            SubmissionItem.objects.create(
                submission=sub,
                item_text=item.text,
                status=status,
                notes=notes
            )
        return redirect('checklists_dashboard')

    return render(request, 'checklists/perform.html', {'checklist': checklist})

@login_required
def onboarding_form(request):
    if request.method == "POST":
        name = request.POST.get('name')
        role = request.POST.get('role')
        start_date = request.POST.get('date')
        reqs = request.POST.get('requirements')
        
        Ticket.objects.create(
            title=f"Onboarding: {name}",
            description=f"New User: {name}\nRole: {role}\nStart Date: {start_date}\nNeeds: {reqs}",
            priority="High",
            created_by=request.user.username,
            status="Open"
        )
        return redirect('ticket_list')

    return render(request, 'checklists/onboarding.html')