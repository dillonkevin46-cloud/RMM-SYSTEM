from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import KnowledgeDocument, DocumentCategory, ManualAsset
from rmm.models import DeviceGroup

@login_required
def kb_dashboard(request):
    documents = KnowledgeDocument.objects.all().order_by('-uploaded_at')
    assets = ManualAsset.objects.all()
    
    context = {
        'documents': documents,
        'assets': assets,
        'categories': DocumentCategory.objects.all(),
        'groups': DeviceGroup.objects.all()
    }
    return render(request, 'knowledge/dashboard.html', context)

@login_required
def upload_document(request):
    if request.method == "POST":
        title = request.POST.get('title')
        cat_id = request.POST.get('category')
        file = request.FILES.get('file')
        
        category = DocumentCategory.objects.get(id=cat_id)
        
        KnowledgeDocument.objects.create(title=title, category=category, file=file)
        return redirect('kb_dashboard')
    
    return redirect('kb_dashboard')

@login_required
def add_manual_asset(request):
    if request.method == "POST":
        ManualAsset.objects.create(
            name=request.POST.get('name'),
            ip_address=request.POST.get('ip'),
            serial_number=request.POST.get('serial'),
            notes=request.POST.get('notes')
        )
        return redirect('kb_dashboard')
    return redirect('kb_dashboard')